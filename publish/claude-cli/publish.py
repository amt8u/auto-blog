#!/usr/bin/env python3
"""CLI publisher: topic -> research -> article -> feature image -> git push.

Usage:
    python3 publish/claude-cli/publish.py "Your topic here"
    python3 publish/claude-cli/publish.py   # prompts interactively

Run translate.py afterwards to add Hindi/Marathi translations.

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
STYLE_FILE = REPO_ROOT / "publish" / "writing-style.md"


def load_system_prompt() -> str:
    """Return SYSTEM_PROMPT with writing-style guide appended if the file exists."""
    style = ""
    if STYLE_FILE.exists():
        style = "\n\n" + STYLE_FILE.read_text(encoding="utf-8")
        log(f"  Loaded writing style: {STYLE_FILE.relative_to(REPO_ROOT)} ({len(style)} chars)")
    else:
        log(f"  Writing style file not found: {STYLE_FILE.relative_to(REPO_ROOT)} (using base prompt only)")
    return SYSTEM_PROMPT + style
POSTS_DIR = REPO_ROOT / "content" / "posts"
IMAGES_DIR = REPO_ROOT / "static" / "images" / "posts"

FRONT_MATTER_RE = re.compile(r"\+\+\+\s*\n(.*?)\n\+\+\+\s*\n", re.DOTALL)
CODE_FENCE_RE = re.compile(r"\A```(?:[\w-]+)?\s*\n(.*?)\n```\s*\Z", re.DOTALL)
SLUG_RE = re.compile(r'^\s*slug\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
TITLE_RE = re.compile(r'^\s*title\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
DESCRIPTION_RE = re.compile(r'^\s*description\s*=\s*"([^"]*)"\s*$', re.MULTILINE)
TAGS_RE = re.compile(r'^\s*tags\s*=\s*\[([^\]]*)\]\s*$', re.MULTILINE)
SVG_BLOCK_RE = re.compile(
    r'<!-- SVG_FILE: ([^\n]+?\.svg) -->\s*\n(<svg[\s\S]+?</svg>)\s*\n<!-- /SVG_FILE -->',
    re.DOTALL,
)
POST_ID_RE = re.compile(r'POST-(\d+)', re.IGNORECASE)


# ---------- utilities ----------

def log(message: str = "", *, file=None) -> None:
    """Print a log line prefixed with [HH:MM:SS]. Preserves leading newlines."""
    ts = datetime.now().strftime("%H:%M:%S")
    leading_nl = ""
    rest = message
    while rest.startswith("\n"):
        leading_nl += "\n"
        rest = rest[1:]
    line = f"{leading_nl}[{ts}] {rest}" if rest else leading_nl
    if file is not None:
        print(line, flush=True, file=file)
    else:
        print(line, flush=True)


# Running totals across all Claude calls in this run.
_usage_totals = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0, "cost": 0.0}


def log_usage(step: str, result_event: dict) -> None:
    """Log token usage and cost from a stream-json `result` event, and accumulate totals."""
    usage = result_event.get("usage") or {}
    inp = usage.get("input_tokens", 0)
    out = usage.get("output_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    cache_creation = usage.get("cache_creation_input_tokens", 0)
    cost = result_event.get("total_cost_usd", 0.0) or 0.0

    _usage_totals["input"] += inp
    _usage_totals["output"] += out
    _usage_totals["cache_read"] += cache_read
    _usage_totals["cache_creation"] += cache_creation
    _usage_totals["cost"] += cost

    parts = [f"in={inp:,}", f"out={out:,}"]
    if cache_read:
        parts.append(f"cache_read={cache_read:,}")
    if cache_creation:
        parts.append(f"cache_write={cache_creation:,}")
    parts.append(f"cost=${cost:.4f}")
    log(f"  Usage [{step}]: {', '.join(parts)}")


def log_usage_total() -> None:
    """Log the accumulated usage across every Claude call in this run."""
    t = _usage_totals
    log(
        f"  Usage [TOTAL]: in={t['input']:,}, out={t['output']:,}, "
        f"cache_read={t['cache_read']:,}, cache_write={t['cache_creation']:,}, "
        f"cost=${t['cost']:.4f}"
    )


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


def next_post_id() -> str:
    """Scan existing posts for the highest POST-XXXX number and return the next one."""
    max_num = 1011  # floor: never go below the existing series
    if POSTS_DIR.exists():
        for p in POSTS_DIR.iterdir():
            m = POST_ID_RE.search(p.name)
            if m:
                max_num = max(max_num, int(m.group(1)))
    return f"POST-{max_num + 1}"


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return text.strip("-")[:80] or "untitled"


def _run_claude_blocking(claude_bin: str, prompt: str, extra_flags: list[str], timeout: int,
                         step: str = "") -> str:
    """Run claude --print and return the result text, or raise RuntimeError.

    If `step` is given, logs token usage / cost from the result event.
    """
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
                if step:
                    log_usage(step, event)
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


def extract_meta(body: str) -> tuple[str, list[str]]:
    """Pull description and tags out of the front matter, for feature image design."""
    front_match = FRONT_MATTER_RE.match(body)
    front = front_match.group(1) if front_match else body
    desc_m = DESCRIPTION_RE.search(front)
    description = desc_m.group(1) if desc_m else ""
    tags_m = TAGS_RE.search(front)
    tags: list[str] = []
    if tags_m:
        tags = [t.strip().strip('"') for t in tags_m.group(1).split(",") if t.strip()]
    return description, tags


# ---------- SVG extraction ----------

def extract_svgs(body: str, slug: str) -> tuple[str, list[Path]]:
    """Replace <!-- SVG_FILE: name.svg -->...<svg>...</svg><!-- /SVG_FILE --> blocks.

    Saves each SVG to static/images/posts/<slug>/name.svg and replaces the
    block with a Markdown image reference. Returns (cleaned_body, saved_paths).
    """
    img_dir = IMAGES_DIR / slug
    saved: list[Path] = []

    def replace(m: re.Match) -> str:
        filename = m.group(1).strip()
        svg_content = m.group(2).strip()
        img_dir.mkdir(parents=True, exist_ok=True)
        out_path = img_dir / filename
        if out_path.exists():
            raise FileExistsError(
                f"Refusing to overwrite existing SVG: {out_path.relative_to(REPO_ROOT)}. "
                f"Pick a different filename or remove the existing file."
            )
        out_path.write_text(svg_content, encoding="utf-8")
        saved.append(out_path)
        alt = filename.rsplit(".", 1)[0].replace("-", " ").replace("_", " ")
        return f"![{alt}](/images/posts/{slug}/{filename})"

    cleaned = SVG_BLOCK_RE.sub(replace, body)
    return cleaned, saved


# ---------- file writing ----------

def write_post(slug: str, body: str, date_prefix: str, post_id: str, lang: str = "") -> Path:
    """Write a new post. Refuses to overwrite an existing file — the publish
    flow only ever creates new posts; modifying an existing one must be a
    deliberate edit (not a silent overwrite from a re-run)."""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f".{lang}.md" if lang else ".md"
    path = POSTS_DIR / f"{date_prefix}-{post_id}-{slug}{suffix}"
    if path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing post: {path.relative_to(REPO_ROOT)}. "
            f"If you meant to update it, edit the file directly. "
            f"Otherwise change the slug or post_id and re-run."
        )
    path.write_text(body, encoding="utf-8")
    return path


# ---------- git ----------

def git_publish(paths: list[Path], title: str, extra_dirs: list[Path] | None = None) -> tuple[str, str | None]:
    def run(*a: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(a, cwd=REPO_ROOT, check=check, capture_output=True, text=True)
    for path in paths:
        run("git", "add", str(path.relative_to(REPO_ROOT)))
    for d in (extra_dirs or []):
        if d.exists():
            run("git", "add", str(d.relative_to(REPO_ROOT)))
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
        "--system-prompt", load_system_prompt(),
        "--allowedTools", "WebSearch,WebFetch",
        "--dangerously-skip-permissions",
        prompt,
    ]

    log(f"[1/4] Researching: {topic[:80]}")

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
                        log(f"\n  Searching: {query}" if query else "\n  Searching...")
            elif etype == "result":
                if event.get("subtype") == "success":
                    result_text = event.get("result", "")
                    print()
                    log_usage("article", event)
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


# ---------- step: feature image ----------

SVG_FENCE_RE = re.compile(r"```(?:svg|xml)?\s*\n(.*?)\n```", re.DOTALL)
SVG_DOC_RE = re.compile(r"<svg[\s\S]*</svg>", re.IGNORECASE)


def design_feature_image_svg(title: str, description: str, tags: list[str], slug: str,
                              post_id: str, claude_bin: str) -> str:
    """Ask Claude to design an original, content-themed feature image SVG.

    Rather than a generic template, Claude designs a visual metaphor specific
    to the article's subject (e.g. a flame chart for a profiling post, a price
    tag + receipts for a pricing comparison, a DNS "phonebook" globe for a DNS
    post). Returns the path to the saved SVG (relative to site root), or "" on
    failure so the caller can proceed without a feature image.
    """
    log("  Designing feature image...")
    tags_str = ", ".join(tags)
    prompt = (
        "Design an original feature image for a blog post, as a single SVG document.\n\n"
        f'Title: "{title}"\n'
        f"Description: {description}\n"
        f"Tags: {tags_str}\n\n"
        "Requirements:\n"
        "- viewBox=\"0 0 1200 630\", no external assets/fonts beyond common families "
        "(Space Grotesk, IBM Plex Mono, Nunito, or generic sans-serif)\n"
        "- Design ONE original visual metaphor that represents the article's core idea "
        "(e.g. a flame chart for a profiling tool, a price tag with receipts for a pricing "
        "comparison, a globe of record cards for a DNS article). Do not use a generic "
        "'dark background with big title text' template.\n"
        "- Do NOT render the post title or any long sentences as text in the image - "
        "small labels (1-3 words, e.g. record types, function names, provider names, "
        "price figures) are fine if they fit the metaphor\n"
        "- Pick a color palette that fits the topic (it does not need to be dark)\n"
        f'- Include a small badge near the bottom with the text "{post_id}" '
        "(e.g. a rounded rect with monospace text)\n"
        "- Include a small \"cloudmato.com\" watermark in a corner\n"
        "- Return ONLY the raw <svg>...</svg> document, no markdown fence, no explanation"
    )
    try:
        result = _run_claude_blocking(
            claude_bin, prompt,
            extra_flags=[],
            timeout=900,
            step="feature-image",
        )
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        log(f"  Feature image design failed: {e}")
        return ""

    svg_content = result.strip()
    fence_m = SVG_FENCE_RE.search(svg_content)
    if fence_m:
        svg_content = fence_m.group(1).strip()

    doc_m = SVG_DOC_RE.search(svg_content)
    if not doc_m:
        log("  Feature image design returned no <svg> document, skipping.")
        return ""
    svg_content = doc_m.group(0)

    img_dir = REPO_ROOT / "static" / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{post_id}-{slug}.svg"
    svg_path = img_dir / filename
    if svg_path.exists():
        log(f"  Feature image already exists, skipping: {svg_path.relative_to(REPO_ROOT)}")
        return f"/images/{filename}"

    svg_path.write_text(svg_content, encoding="utf-8")
    relative_path = f"/images/{filename}"
    log(f"  ✓ Generated feature image: {relative_path}")
    return relative_path


def inject_feature_image(body: str, image_url: str) -> str:
    """Insert feature_image into the TOML front matter if not already present.

    Scopes the "already present" check to the entire front matter block (not
    just body[:600]) — otherwise long front matter can hide an existing
    feature_image and end up with a duplicate TOML key.
    """
    if not image_url:
        return body
    front_match = FRONT_MATTER_RE.match(body)
    if front_match and re.search(r'^\s*feature_image\s*=', front_match.group(1), re.MULTILINE):
        return body
    # Replace the closing +++ of the front matter (first occurrence after opening)
    return re.sub(
        r'(\n\+\+\+)',
        f'\nfeature_image = "{image_url}"\n+++',
        body,
        count=1,
    )


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
            log("No topic provided.", file=sys.stderr)
            sys.exit(1)

    try:
        claude_bin = find_claude()
    except FileNotFoundError as e:
        log(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 1: Generate article
    try:
        raw = generate_article(topic, claude_bin)
    except RuntimeError as e:
        log(f"\nGeneration failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Always persist the raw response before parsing — if parse fails (e.g. Claude
    # returned a summary instead of the article), the user can recover manually
    # rather than losing whatever the API call cost.
    recovery_path = REPO_ROOT / "publish" / ".last-raw.md"
    try:
        recovery_path.write_text(raw, encoding="utf-8")
        log(f"  Raw response saved: {recovery_path.relative_to(REPO_ROOT)} ({len(raw):,} chars)")
    except OSError as e:
        log(f"  Warning: could not save raw response: {e}")

    try:
        slug, title, body = parse_article(raw)
    except ValueError as e:
        log(f"\nParse failed: {e}", file=sys.stderr)
        log(
            f"\nThe raw model output was saved to {recovery_path.relative_to(REPO_ROOT)}. "
            f"You can edit it by hand (prepend the +++ front matter block) and then move "
            f"it into content/posts/ to recover the generation.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 2: Extract SVG diagrams
    log("[2/4] Extracting diagrams...")
    body, svg_paths = extract_svgs(body, slug)
    if svg_paths:
        log(f"  Extracted {len(svg_paths)} diagram(s): {[p.name for p in svg_paths]}")
    else:
        log("  No diagrams found.")

    post_id = next_post_id()
    log(f"  Assigned: {post_id}")

    # Step 3: Write the post file
    log("[3/4] Writing file...")
    date_prefix = datetime.now().strftime("%Y-%m-%d")

    path_en = write_post(slug, body, date_prefix, post_id)
    log(f"Written: {path_en.relative_to(REPO_ROOT)}")

    # Step 4: Generate feature image, then inject it into the post just written
    log("[4/4] Generating feature image...")
    description, tags = extract_meta(body)
    image_url = design_feature_image_svg(title, description, tags, slug, post_id, claude_bin)
    if image_url:
        body = inject_feature_image(body, image_url)
        path_en.write_text(body, encoding="utf-8")

    log("Committing and pushing...")
    img_dir = IMAGES_DIR / slug if svg_paths else None
    extra_dirs = [img_dir] if img_dir else None
    paths = [path_en]
    if image_url:
        paths.append(REPO_ROOT / "static" / image_url.lstrip("/"))
    sha, push_err = git_publish(paths, title, extra_dirs=extra_dirs)
    if push_err:
        log(f"Committed {sha[:8]} locally. Push failed:\n  {push_err}")
    else:
        log(f'Done! "{title}" [{post_id}] pushed as commit {sha[:8]}.')
        log(f"  EN: /posts/{slug}/")
        log("  Run translate.py to add Hindi/Marathi translations.")

    log_usage_total()


if __name__ == "__main__":
    main()
