#!/usr/bin/env python3
"""CLI publisher: topic -> research -> article -> feature image -> Hindi translation -> git push.

Usage:
    python3 publish/claude-cli/publish.py "Your topic here"
    python3 publish/claude-cli/publish.py   # prompts interactively

Requires the Claude Code CLI (claude) authenticated with your claude.ai subscription.
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


# ---------- utilities ----------

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


def _run_claude_blocking(claude_bin: str, prompt: str, extra_flags: list[str], timeout: int) -> str:
    """Run claude --print and return the result text, or raise RuntimeError."""
    cmd = [
        claude_bin, "--print", "--verbose",
        "--output-format", "stream-json",
        "--dangerously-skip-permissions",
        *extra_flags,
        prompt,
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout,
    )
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
            if event.get("type") == "result" and event.get("subtype") == "success":
                return event.get("result", "").strip()
        except json.JSONDecodeError:
            continue
    if result.returncode != 0:
        raise RuntimeError(result.stderr[:300] or "no output")
    return ""


# ---------- parsing ----------

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


# ---------- file writing ----------

def write_post(slug: str, body: str, date_prefix: str, lang: str = "") -> Path:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f".{lang}.md" if lang else ".md"
    path = POSTS_DIR / f"{date_prefix}-{slug}{suffix}"
    path.write_text(body, encoding="utf-8")
    return path


# ---------- git ----------

def git_publish(paths: list[Path], title: str) -> tuple[str, str | None]:
    def run(*a: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(a, cwd=REPO_ROOT, check=check, capture_output=True, text=True)
    for path in paths:
        run("git", "add", str(path.relative_to(REPO_ROOT)))
    run("git", "commit", "-m", f"post: {title}")
    sha = run("git", "rev-parse", "HEAD").stdout.strip()
    push = run("git", "push", check=False)
    err = push.stderr.strip() if push.returncode != 0 else None
    return sha, err


# ---------- step 1: generate article ----------

def generate_article(topic: str, claude_bin: str) -> str:
    iso_date = datetime.now().astimezone().isoformat(timespec="seconds")
    prompt = user_prompt(topic, iso_date)

    cmd = [
        claude_bin, "--print", "--verbose",
        "--output-format", "stream-json",
        "--system-prompt", SYSTEM_PROMPT,
        "--allowedTools", "WebSearch,WebFetch",
        "--dangerously-skip-permissions",
        prompt,
    ]

    print(f"[1/3] Researching: {topic[:80]}", flush=True)

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=REPO_ROOT,
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
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "text":
                        chunk = block.get("text", "")
                        chars_written += len(chunk)
                        if chars_written // 200 != (chars_written - len(chunk)) // 200:
                            print(".", end="", flush=True)
                    elif block.get("type") == "tool_use":
                        query = block.get("input", {}).get("query", "")
                        print(f"\n  Searching: {query}" if query else "\n  Searching...", flush=True)
            elif etype == "result":
                if event.get("subtype") == "success":
                    result_text = event.get("result", "")
                    print()
                elif event.get("subtype") == "error":
                    raise RuntimeError(f"Claude error: {event.get('result', 'unknown')}")
    finally:
        proc.wait()

    if proc.returncode != 0:
        stderr_out = proc.stderr.read() if proc.stderr else ""
        raise RuntimeError(f"claude CLI exited {proc.returncode}: {stderr_out[:400]}")
    if not result_text:
        raise RuntimeError("Claude returned empty output.")
    return result_text.strip()


# ---------- step 2: feature image ----------

def find_feature_image(title: str, claude_bin: str) -> str:
    """Search for a freely available image and return its URL, or empty string."""
    print("[2/3] Finding feature image...", flush=True)
    prompt = (
        f'Find one freely available, high-quality photo for a blog post titled: "{title}". '
        f'Search Unsplash (images.unsplash.com) for a relevant image. '
        f'Return ONLY the direct image URL starting with https://images.unsplash.com/photo-, '
        f'with ?w=1200 appended. Nothing else — no explanation, no markdown. '
        f'If no suitable image is found, return exactly: NONE'
    )
    try:
        url = _run_claude_blocking(
            claude_bin, prompt,
            extra_flags=["--allowedTools", "WebSearch,WebFetch"],
            timeout=120,
        )
    except (RuntimeError, subprocess.TimeoutExpired):
        return ""

    # Accept only clean Unsplash or other https image URLs
    url = url.strip().strip('"').strip("'")
    if url == "NONE" or not url.startswith("https://"):
        print("  No image found, skipping.", flush=True)
        return ""
    print(f"  Image: {url[:70]}", flush=True)
    return url


def inject_feature_image(body: str, image_url: str) -> str:
    """Insert feature_image into the TOML front matter if not already present."""
    if not image_url or "feature_image" in body[:600]:
        return body
    # Replace the closing +++ of the front matter (first occurrence after opening)
    return re.sub(
        r'(\n\+\+\+)',
        f'\nfeature_image = "{image_url}"\n+++',
        body,
        count=1,
    )


# ---------- step 3: translate ----------

def translate_to_hindi(body: str, slug: str, claude_bin: str) -> str | None:
    """Translate article to Hindi. Returns translated body or None on failure."""
    print("[3/3] Translating to Hindi...", flush=True)
    prompt = (
        "Translate this Hugo blog post to Hindi.\n\n"
        "Rules:\n"
        f'- Keep slug exactly as: "{slug}"\n'
        f'- Change canonical to "/hi/posts/{slug}/"\n'
        "- Translate title, description, tags, keywords, and all body text to Hindi\n"
        "- Keep date, feature_image, and all other non-text front matter fields unchanged\n"
        "- Keep all Markdown formatting intact (## headings, **bold**, links, tables, `code`)\n"
        "- Do NOT add an H1 heading in the body\n"
        "- Return ONLY the translated document starting with +++, no preamble or explanation\n\n"
        f"{body}"
    )
    try:
        result = _run_claude_blocking(claude_bin, prompt, extra_flags=[], timeout=300)
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        print(f"  Translation failed: {e}", flush=True)
        return None

    # Strip accidental code fence
    if result.startswith("```"):
        lines = result.split("\n")
        result = "\n".join(lines[1:-1]).strip()

    if not result.startswith("+++"):
        print("  Translation returned unexpected format, skipping.", flush=True)
        return None

    print("  Done.", flush=True)
    return result


# ---------- main ----------

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

    # Step 1: Generate article
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

    # Step 2: Feature image
    image_url = find_feature_image(title, claude_bin)
    body = inject_feature_image(body, image_url)

    # Step 3: Translate to Hindi
    hindi_body = translate_to_hindi(body, slug, claude_bin)

    # Write files
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    paths: list[Path] = []

    path_en = write_post(slug, body, date_prefix)
    paths.append(path_en)
    print(f"Written: {path_en.relative_to(REPO_ROOT)}")

    if hindi_body:
        path_hi = write_post(slug, hindi_body, date_prefix, lang="hi")
        paths.append(path_hi)
        print(f"Written: {path_hi.relative_to(REPO_ROOT)}")

    # Commit and push everything in one commit
    print("Committing and pushing...", flush=True)
    sha, push_err = git_publish(paths, title)
    if push_err:
        print(f"Committed {sha[:8]} locally. Push failed:\n  {push_err}")
    else:
        print(f'Done! "{title}" pushed as commit {sha[:8]}.')
        if hindi_body:
            print(f"  EN: /posts/{slug}/")
            print(f"  HI: /hi/posts/{slug}/")


if __name__ == "__main__":
    main()
