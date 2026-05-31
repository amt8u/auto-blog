"""Local-only publisher: Flask form -> Claude (streaming + web_search) -> Markdown -> git.

Run:
    publish/api-key/.venv/bin/python publish/api-key/publish.py

Opens http://localhost:5000 — paste a topic, click publish. Progress streams live.

Requires an Anthropic API key in publish/api-key/.env:
    ANTHROPIC_API_KEY=sk-ant-...
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, Response, render_template_string, request

from prompts import SYSTEM_PROMPT, user_prompt

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POSTS_DIR = REPO_ROOT / "content" / "posts"
IMAGES_DIR = REPO_ROOT / "static" / "images" / "posts"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8096
MAX_SEARCHES = 5

SVG_BLOCK_RE = re.compile(
    r'<!-- SVG_FILE: ([^\n]+?\.svg) -->\s*\n(<svg[\s\S]+?</svg>)\s*\n<!-- /SVG_FILE -->',
    re.DOTALL,
)

load_dotenv(Path(__file__).parent / ".env")
client = Anthropic()
app = Flask(__name__)


# ---------- parse ----------

FRONT_MATTER_RE = re.compile(r"\+\+\+\s*\n(.*?)\n\+\+\+\s*\n", re.DOTALL)
CODE_FENCE_RE = re.compile(r"\A```(?:[\w-]+)?\s*\n(.*?)\n```\s*\Z", re.DOTALL)
SLUG_RE = re.compile(r'^\s*slug\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
TITLE_RE = re.compile(r'^\s*title\s*=\s*"([^"]+)"\s*$', re.MULTILINE)


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return text.strip("-")[:80] or "untitled"


def parse_article(raw: str) -> tuple[str, str, str]:
    """Extract (slug, title, article_text) from Claude's response.

    Tolerates: leading preamble, trailing trailer, enclosing ```markdown/```toml fence.
    """
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


def extract_svgs(body: str, slug: str) -> tuple[str, list[Path]]:
    """Replace SVG blocks with Markdown image references and save SVG files."""
    img_dir = IMAGES_DIR / slug
    saved: list[Path] = []

    def replace(m: re.Match) -> str:
        filename = m.group(1).strip()
        svg_content = m.group(2).strip()
        img_dir.mkdir(parents=True, exist_ok=True)
        out_path = img_dir / filename
        out_path.write_text(svg_content, encoding="utf-8")
        saved.append(out_path)
        alt = filename.rsplit(".", 1)[0].replace("-", " ").replace("_", " ")
        return f"![{alt}](/images/posts/{slug}/{filename})"

    cleaned = SVG_BLOCK_RE.sub(replace, body)
    return cleaned, saved


def write_post(slug: str, body: str) -> tuple[Path, list[Path]]:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    body, svg_paths = extract_svgs(body, slug)
    path = POSTS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}-{slug}.md"
    path.write_text(body, encoding="utf-8")
    return path, svg_paths


# ---------- git ----------

def git_publish(path: Path, title: str, svg_paths: list[Path] | None = None) -> tuple[str, str | None]:
    """Commit + push. Returns (sha, push_error_or_None)."""
    def run(*a: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(a, cwd=REPO_ROOT, check=check, capture_output=True, text=True)

    run("git", "add", str(path.relative_to(REPO_ROOT)))
    if svg_paths:
        slug = svg_paths[0].parent.name
        img_dir = IMAGES_DIR / slug
        if img_dir.exists():
            run("git", "add", str(img_dir.relative_to(REPO_ROOT)))
    run("git", "commit", "-m", f"post: {title}")
    sha = run("git", "rev-parse", "HEAD").stdout.strip()
    push = run("git", "push", check=False)
    err = push.stderr.strip() if push.returncode != 0 else None
    return sha, err


# ---------- streaming (SSE) ----------

def sse(event_type: str, **data: Any) -> str:
    """Format one SSE event."""
    return f"data: {json.dumps({'type': event_type, **data})}\n\n"


def stream_generation(topic: str) -> Iterator[str]:
    """Yield SSE-formatted progress events while Claude researches and writes."""
    iso_date = datetime.now().astimezone().isoformat(timespec="seconds")
    yield sse("log", message=f"Starting research on: {topic[:120]}")

    # Buffers to assemble the final text and to track the in-flight tool input.
    full_text_parts: list[str] = []
    tool_input_buffers: dict[int, str] = {}  # index -> accumulating JSON for that block
    text_chars = 0

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": MAX_SEARCHES,
            }],
            messages=[{"role": "user", "content": user_prompt(topic, iso_date)}],
        ) as stream:
            for event in stream:
                et = event.type

                if et == "content_block_start":
                    block = event.content_block
                    btype = getattr(block, "type", None)
                    if btype == "server_tool_use" and getattr(block, "name", "") == "web_search":
                        tool_input_buffers[event.index] = ""
                        yield sse("log", message="Preparing web search…")
                    elif btype == "web_search_tool_result":
                        results = getattr(block, "content", []) or []
                        n = len(results) if isinstance(results, list) else 0
                        titles = []
                        if isinstance(results, list):
                            for r in results[:3]:
                                t = getattr(r, "title", None) or (r.get("title") if isinstance(r, dict) else None)
                                if t:
                                    titles.append(t)
                        msg = f"Got {n} result(s)"
                        if titles:
                            msg += ": " + " · ".join(titles)
                        yield sse("search_result", message=msg, count=n)
                    elif btype == "text":
                        yield sse("log", message="Writing article…")

                elif et == "content_block_delta":
                    delta = event.delta
                    dtype = getattr(delta, "type", None)
                    if dtype == "input_json_delta":
                        tool_input_buffers[event.index] = tool_input_buffers.get(event.index, "") + getattr(delta, "partial_json", "")
                    elif dtype == "text_delta":
                        chunk = getattr(delta, "text", "") or ""
                        full_text_parts.append(chunk)
                        text_chars += len(chunk)
                        # Throttle progress pings: emit every ~200 chars.
                        if text_chars and text_chars // 200 != (text_chars - len(chunk)) // 200:
                            yield sse("progress", chars=text_chars)

                elif et == "content_block_stop":
                    buf = tool_input_buffers.pop(event.index, None)
                    if buf is not None:
                        try:
                            parsed = json.loads(buf)
                            query = parsed.get("query") if isinstance(parsed, dict) else None
                            if query:
                                yield sse("search_start", query=query)
                        except json.JSONDecodeError:
                            pass

                # Other events (message_start, message_delta, message_stop) -> ignored.

    except Exception as e:
        app.logger.exception("Claude stream failed")
        yield sse("error", message=f"{type(e).__name__}: {e}")
        return

    raw = "".join(full_text_parts).strip()
    if not raw:
        yield sse("error", message="Claude returned no text content.")
        return

    yield sse("log", message=f"Parsing response ({text_chars} chars)…")
    try:
        slug, title, body = parse_article(raw)
    except ValueError as e:
        yield sse("error", message=str(e))
        return

    path, svg_paths = write_post(slug, body)
    yield sse("log", message=f"Wrote {path.relative_to(REPO_ROOT)}")
    if svg_paths:
        yield sse("log", message=f"Saved {len(svg_paths)} diagram(s): {[p.name for p in svg_paths]}")

    yield sse("log", message="Committing…")
    sha, push_err = git_publish(path, title, svg_paths=svg_paths)
    if push_err:
        yield sse("log", message=f"Local commit {sha[:8]} created. Push skipped: {push_err}")
    else:
        yield sse("log", message=f"Pushed commit {sha[:8]}")

    yield sse(
        "done",
        slug=slug,
        title=title,
        path=str(path.relative_to(REPO_ROOT)),
        sha=sha[:8],
        preview_url=f"http://localhost:1313/posts/{slug}/",
    )


# ---------- routes ----------

FORM_HTML = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>Auto Blog — New Post</title>
<style>
 body{font:16px/1.5 system-ui,-apple-system,sans-serif;max-width:760px;margin:3rem auto;padding:0 1rem;color:#222}
 h1{margin:0 0 .25rem}p.sub{color:#666;margin:0 0 1.5rem}
 textarea{width:100%;min-height:160px;padding:.75rem;font:inherit;border:1px solid #ccc;border-radius:6px;box-sizing:border-box}
 button{margin-top:.75rem;padding:.6rem 1.2rem;font:inherit;background:#222;color:#fff;border:0;border-radius:6px;cursor:pointer}
 button:disabled{opacity:.5;cursor:wait}
 #log{margin-top:1.5rem;padding:1rem;background:#0f1419;color:#cfd5dc;border-radius:6px;font:13px/1.55 ui-monospace,Menlo,monospace;white-space:pre-wrap;min-height:0;max-height:60vh;overflow:auto;display:none}
 #log.show{display:block}
 #log .ev-search_start{color:#7fd9ff}
 #log .ev-search_result{color:#9ee37d}
 #log .ev-progress{color:#888}
 #log .ev-error{color:#ff8b8b}
 #log .ev-done{color:#9ee37d;font-weight:600}
 #log .ev-log{color:#cfd5dc}
 #log a{color:#9ee37d}
 .spin{display:inline-block;width:10px;height:10px;border:2px solid #444;border-top-color:#9ee37d;border-radius:50%;animation:spin 1s linear infinite;vertical-align:-1px;margin-right:6px}
 @keyframes spin{to{transform:rotate(360deg)}}
</style></head><body>
<h1>Auto Blog</h1>
<p class="sub">Type a topic. Claude researches with web search, writes a cited article, and publishes it.</p>
<form id="f">
  <textarea name="topic" id="topic" placeholder="e.g. The history of the bicycle, focused on the safety bicycle era" required></textarea>
  <button type="submit" id="go">Research & Publish</button>
</form>
<div id="log" aria-live="polite"></div>
<script>
const f = document.getElementById('f');
const topicEl = document.getElementById('topic');
const go = document.getElementById('go');
const log = document.getElementById('log');

function append(cls, html, withSpin) {
  const line = document.createElement('div');
  line.className = 'ev-' + cls;
  line.innerHTML = (withSpin ? '<span class="spin"></span>' : '') + html;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

function escapeHTML(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

f.addEventListener('submit', (e) => {
  e.preventDefault();
  const topic = topicEl.value.trim();
  if (!topic) return;
  go.disabled = true; go.textContent = 'Researching…';
  log.classList.add('show'); log.innerHTML = '';
  append('log', 'Connecting…', true);

  const es = new EventSource('/stream?topic=' + encodeURIComponent(topic));
  es.onmessage = (msg) => {
    const ev = JSON.parse(msg.data);
    if (ev.type === 'search_start') append('search_start', '🔎 Searching: ' + escapeHTML(ev.query));
    else if (ev.type === 'search_result') append('search_result', '✓ ' + escapeHTML(ev.message));
    else if (ev.type === 'progress') append('progress', '… ' + ev.chars + ' chars written');
    else if (ev.type === 'log') append('log', escapeHTML(ev.message));
    else if (ev.type === 'error') { append('error', '✗ ' + escapeHTML(ev.message)); es.close(); go.disabled = false; go.textContent = 'Research & Publish'; }
    else if (ev.type === 'done') {
      append('done', '✓ Published "' + escapeHTML(ev.title) + '" — <a href="' + ev.preview_url + '" target="_blank">' + ev.preview_url + '</a> (commit ' + ev.sha + ')');
      es.close();
      go.disabled = false; go.textContent = 'Research & Publish';
      topicEl.value = '';
    }
  };
  es.onerror = () => { append('error', '✗ Connection lost.'); es.close(); go.disabled = false; go.textContent = 'Research & Publish'; };
});
</script>
</body></html>
"""


@app.get("/")
def home():
    return render_template_string(FORM_HTML)


@app.get("/stream")
def stream():
    topic = (request.args.get("topic") or "").strip()
    if not topic:
        return Response(sse("error", message="Topic is required."), mimetype="text/event-stream")
    return Response(
        stream_generation(topic),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    # threaded=True so SSE streams don't block other requests.
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
