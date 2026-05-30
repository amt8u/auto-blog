#!/usr/bin/env python3
"""CLI publisher: topic -> Claude (web search) -> Markdown -> git push.

Usage:
    python publish/publish.py "Your topic here"
    python publish/publish.py           # prompts interactively

Requires the Claude Code CLI (claude) to be installed and authenticated
with your claude.ai subscription — no API key needed.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from prompts import SYSTEM_PROMPT, user_prompt

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POSTS_DIR = REPO_ROOT / "content" / "posts"

FRONT_MATTER_RE = re.compile(r"\+\+\+\s*\n(.*?)\n\+\+\+\s*\n", re.DOTALL)
CODE_FENCE_RE = re.compile(r"\A```(?:[\w-]+)?\s*\n(.*?)\n```\s*\Z", re.DOTALL)
SLUG_RE = re.compile(r'^\s*slug\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
TITLE_RE = re.compile(r'^\s*title\s*=\s*"([^"]+)"\s*$', re.MULTILINE)


def find_claude() -> str:
    found = shutil.which("claude")
    if found:
        return found
    ext_dir = Path.home() / ".vscode" / "extensions"
    if ext_dir.exists():
        matches = sorted(ext_dir.glob("anthropic.claude-code-*/resources/native-binary/claude"))
        for p in reversed(matches):
            if p.is_file() and os.access(str(p), os.X_OK):
                return str(p)
    raise FileNotFoundError(
        "Cannot find the claude CLI.\n"
        "Install Claude Code from https://claude.ai/code and make sure it's on PATH."
    )


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return text.strip("-")[:80] or "untitled"


def parse_article(raw: str) -> tuple[str, str, str]:
    text = raw.strip()
    fence = CODE_FENCE_RE.match(text)
    if fence:
        text = fence.group(1).strip()
    m = FRONT_MATTER_RE.search(text)
    if not m:
        raise ValueError(
            "Response is missing a TOML front matter block (+++ ... +++).\n\n"
            "First 500 chars of response:\n" + text[:500]
        )
    article = text[m.start():]
    front = m.group(1)
    title_m = TITLE_RE.search(front)
    if not title_m:
        raise ValueError("Front matter is missing `title`.")
    title = title_m.group(1)
    slug_m = SLUG_RE.search(front)
    slug = slug_m.group(1) if slug_m else slugify(title)
    return slug, title, article


def write_post(slug: str, body: str) -> Path:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    path = POSTS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}-{slug}.md"
    path.write_text(body, encoding="utf-8")
    return path


def git_publish(path: Path, title: str) -> tuple[str, str | None]:
    def run(*a: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(a, cwd=REPO_ROOT, check=check, capture_output=True, text=True)
    run("git", "add", str(path.relative_to(REPO_ROOT)))
    run("git", "commit", "-m", f"post: {title}")
    sha = run("git", "rev-parse", "HEAD").stdout.strip()
    push = run("git", "push", check=False)
    err = push.stderr.strip() if push.returncode != 0 else None
    return sha, err


def generate_article(topic: str, claude_bin: str) -> str:
    iso_date = datetime.now().astimezone().isoformat(timespec="seconds")
    prompt = user_prompt(topic, iso_date)

    cmd = [
        claude_bin,
        "--print",
        "--verbose",
        "--output-format", "stream-json",
        "--system-prompt", SYSTEM_PROMPT,
        "--allowedTools", "WebSearch,WebFetch",
        "--dangerously-skip-permissions",
        prompt,
    ]

    print(f"Researching: {topic[:80]}", flush=True)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=REPO_ROOT,
    )

    result_text = ""
    chars_written = 0

    try:
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = event.get("type")

            if etype == "assistant":
                content = event.get("message", {}).get("content", [])
                for block in content:
                    btype = block.get("type")
                    if btype == "text":
                        chunk = block.get("text", "")
                        chars_written += len(chunk)
                        # Print a dot every ~200 chars to show progress
                        if chars_written // 200 != (chars_written - len(chunk)) // 200:
                            print(".", end="", flush=True)
                    elif btype == "tool_use":
                        query = block.get("input", {}).get("query", "")
                        label = f" ({query})" if query else ""
                        print(f"\n  Searching{label}", flush=True)

            elif etype == "result":
                subtype = event.get("subtype", "")
                if subtype == "success":
                    result_text = event.get("result", "")
                    print()
                elif subtype == "error":
                    raise RuntimeError(f"Claude error: {event.get('result', 'unknown')}")

    finally:
        proc.wait()

    if proc.returncode != 0:
        stderr_out = proc.stderr.read() if proc.stderr else ""
        raise RuntimeError(f"claude CLI exited {proc.returncode}: {stderr_out[:400]}")

    if not result_text:
        raise RuntimeError("Claude returned empty output.")

    return result_text.strip()


def main() -> None:
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        try:
            topic = input("Topic: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        if not topic:
            print("No topic provided.", file=sys.stderr)
            sys.exit(1)

    try:
        claude_bin = find_claude()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        raw = generate_article(topic, claude_bin)
    except RuntimeError as e:
        print(f"\nGeneration failed: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        slug, title, body = parse_article(raw)
    except ValueError as e:
        print(f"\nParse failed: {e}", file=sys.stderr)
        sys.exit(1)

    path = write_post(slug, body)
    print(f"Written: {path.relative_to(REPO_ROOT)}")

    print("Committing and pushing...", flush=True)
    sha, push_err = git_publish(path, title)
    if push_err:
        print(f"Committed {sha[:8]} locally. Push failed:\n  {push_err}")
    else:
        print(f"Done! \"{title}\" pushed as commit {sha[:8]}.")


if __name__ == "__main__":
    main()
