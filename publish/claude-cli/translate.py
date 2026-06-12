#!/usr/bin/env python3
"""Standalone translation flow: pick a post by number, pick a language, translate, commit, push.

Usage:
    python3 publish/claude-cli/translate.py
    python3 publish/claude-cli/translate.py 1053
    python3 publish/claude-cli/translate.py 1053 hindi

Requires the Claude Code CLI (claude) authenticated with your claude.ai subscription.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from publish import (
    REPO_ROOT,
    POSTS_DIR,
    _run_claude_blocking,
    find_claude,
    git_publish,
    log,
    log_usage_total,
    write_post,
)

DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-POST-(\d+)-(.+)\.md$")


def _report_bad_translation(result: str, slug: str, lang_code: str) -> None:
    """Log diagnostics for an unexpected translation result and save it for inspection."""
    log(f"  Translation returned unexpected format ({len(result):,} chars).")
    if not result:
        log("  Result was empty.")
        return None

    preview_len = 300
    head = result[:preview_len]
    log(f"  First {len(head)} chars:\n{head}")
    if len(result) > preview_len:
        tail = result[-preview_len:]
        log(f"  Last {len(tail)} chars:\n{tail}")

    recovery_path = REPO_ROOT / "publish" / f".last-translate-{lang_code}-{slug}.md"
    try:
        recovery_path.write_text(result, encoding="utf-8")
        log(f"  Full output saved to: {recovery_path.relative_to(REPO_ROOT)}")
    except OSError as e:
        log(f"  Warning: could not save raw output: {e}")

    return None


def translate_to_hindi(body: str, slug: str, claude_bin: str) -> str | None:
    """Translate article to Hindi. Returns translated body or None on failure."""
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
        result = _run_claude_blocking(claude_bin, prompt, extra_flags=[], timeout=1500, step="translate-hi")
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        log(f"  Translation failed: {e}")
        return None

    # Strip accidental code fence
    if result.startswith("```"):
        lines = result.split("\n")
        result = "\n".join(lines[1:-1]).strip()

    if not result.startswith("+++"):
        return _report_bad_translation(result, slug, "hi")

    log("  Done.")
    return result


def translate_to_marathi(body: str, slug: str, claude_bin: str) -> str | None:
    """Translate article to Marathi. Returns translated body or None on failure."""
    prompt = (
        "Translate this Hugo blog post to Marathi.\n\n"
        "Rules:\n"
        f'- Keep slug exactly as: "{slug}"\n'
        f'- Change canonical to "/mr/posts/{slug}/"\n'
        "- Translate title, description, and all body text to Marathi\n"
        "- Keep tags in English (same values as the original)\n"
        "- Keep date, feature_image, and all other non-text front matter fields unchanged\n"
        "- Keep all Markdown formatting intact (## headings, **bold**, links, tables, `code`)\n"
        "- Do NOT add an H1 heading in the body\n"
        "- Return ONLY the translated document starting with +++, no preamble or explanation\n\n"
        f"{body}"
    )
    try:
        result = _run_claude_blocking(claude_bin, prompt, extra_flags=[], timeout=1500, step="translate-mr")
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        log(f"  Translation failed: {e}")
        return None

    if result.startswith("```"):
        lines = result.split("\n")
        result = "\n".join(lines[1:-1]).strip()

    if not result.startswith("+++"):
        return _report_bad_translation(result, slug, "mr")

    log("  Done.")
    return result


LANGUAGES = {
    "hindi": {"code": "hi", "label": "Hindi", "translate": translate_to_hindi},
    "marathi": {"code": "mr", "label": "Marathi", "translate": translate_to_marathi},
}


def find_post(post_number: str) -> tuple[Path, str, str, str]:
    """Find the English post file for a given post number.

    Returns (path, date_prefix, post_id, slug).
    """
    pattern = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}-POST-{post_number}-.+\.md$", re.IGNORECASE)
    matches = [p for p in POSTS_DIR.iterdir() if pattern.match(p.name)]
    if not matches:
        raise FileNotFoundError(f"No English post found for POST-{post_number} in {POSTS_DIR}")
    if len(matches) > 1:
        raise FileNotFoundError(
            f"Multiple English posts found for POST-{post_number}: "
            f"{[m.name for m in matches]}"
        )
    path = matches[0]
    m = DATE_PREFIX_RE.match(path.name)
    if not m:
        raise ValueError(f"Could not parse filename: {path.name}")
    date_prefix, num, slug = m.groups()
    return path, date_prefix, f"POST-{num}", slug


def prompt_post_number() -> str:
    try:
        value = input("Post number (e.g. 1053): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    if not value:
        log("No post number provided.", file=sys.stderr)
        sys.exit(1)
    return value


def prompt_language() -> str:
    options = list(LANGUAGES.keys())
    print("Translate to:")
    for i, key in enumerate(options, start=1):
        print(f"  {i}. {LANGUAGES[key]['label']}")
    try:
        choice = input(f"Choose [1-{len(options)}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        return options[int(choice) - 1]
    choice_lower = choice.lower()
    if choice_lower in LANGUAGES:
        return choice_lower
    log(f"Invalid choice: {choice!r}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    args = sys.argv[1:]

    post_number = args[0] if len(args) > 0 else prompt_post_number()
    post_number = re.sub(r"[^0-9]", "", post_number)

    try:
        path_en, date_prefix, post_id, slug = find_post(post_number)
    except (FileNotFoundError, ValueError) as e:
        log(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log(f"Found: {path_en.relative_to(REPO_ROOT)} ({post_id})")

    lang_key = args[1].lower() if len(args) > 1 else prompt_language()
    if lang_key not in LANGUAGES:
        log(f"Error: unknown language {lang_key!r}", file=sys.stderr)
        sys.exit(1)
    lang = LANGUAGES[lang_key]

    try:
        claude_bin = find_claude()
    except FileNotFoundError as e:
        log(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    body = path_en.read_text(encoding="utf-8")

    log(f"Translating {post_id} to {lang['label']}...")
    translated = lang["translate"](body, slug, claude_bin)
    if not translated:
        log(f"\nAborting: {lang['label']} translation failed. Nothing was committed or pushed.", file=sys.stderr)
        sys.exit(1)

    path_out = write_post(slug, translated, date_prefix, post_id, lang=lang["code"])
    log(f"Written: {path_out.relative_to(REPO_ROOT)}")

    log("Committing and pushing...")
    title_m = re.search(r'^\s*title\s*=\s*"([^"]+)"\s*$', body, re.MULTILINE)
    title = title_m.group(1) if title_m else slug
    sha, push_err = git_publish([path_out], f"{title} ({lang['label']})")
    if push_err:
        log(f"Committed {sha[:8]} locally. Push failed:\n  {push_err}")
    else:
        log(f"Done! {post_id} translated to {lang['label']} and pushed as commit {sha[:8]}.")
        log(f"  {lang['code'].upper()}: /{lang['code']}/posts/{slug}/")

    log_usage_total()


if __name__ == "__main__":
    main()
