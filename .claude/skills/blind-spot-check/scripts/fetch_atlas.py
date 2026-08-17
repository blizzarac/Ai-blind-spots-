#!/usr/bin/env python3
"""Fetch Blind Spot Atlas entries and print them as markdown for context use.

Resolution order: live atlas -> ~/.cache copy (24h TTL) -> bundled snapshot.
Python 3.8+, stdlib only.

Examples:
    fetch_atlas.py --list
    fetch_atlas.py --categories confabulation,reasoning-shortcuts
    fetch_atlas.py --ids invented-apis --format full
    fetch_atlas.py --all --format brief
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

DEFAULT_URL = "https://blizzarac.github.io/Ai-blind-spots-/atlas.json"
CACHE_PATH = Path.home() / ".cache" / "blind-spot-atlas" / "atlas.json"
CACHE_TTL_SECONDS = 24 * 3600
SNAPSHOT_PATH = Path(__file__).resolve().parent.parent / "assets" / "atlas-snapshot.json"


def load_atlas(url: str, no_cache: bool):
    """Return (atlas_dict, source_description). Never raises on network failure."""
    if "://" not in url:  # local file path
        return json.loads(Path(url).read_text(encoding="utf-8")), f"local file {url}"

    if not no_cache and CACHE_PATH.exists():
        age = time.time() - CACHE_PATH.stat().st_mtime
        if age < CACHE_TTL_SECONDS:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8")), "cache (<24h old)"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
        atlas = json.loads(raw)
        try:
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            CACHE_PATH.write_text(raw, encoding="utf-8")
        except OSError:
            pass  # cache is best-effort
        return atlas, "live"
    except Exception as exc:  # URLError, timeout, JSON error, proxy block...
        if CACHE_PATH.exists():
            return (
                json.loads(CACHE_PATH.read_text(encoding="utf-8")),
                f"STALE cache — live fetch failed ({exc})",
            )
        atlas = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        return atlas, (
            f"BUNDLED SNAPSHOT generated {atlas.get('generated', 'unknown')} — "
            f"live fetch failed ({exc})"
        )


def html_to_markdown(body_html: str) -> str:
    """Lightweight HTML->markdown for entry bodies (h2/h3, p, li, code, pre)."""
    s = body_html
    s = re.sub(r"<pre[^>]*><code[^>]*>(.*?)</code></pre>", lambda m: "\n```\n" + html.unescape(m.group(1)) + "```\n", s, flags=re.DOTALL)
    s = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", s, flags=re.DOTALL)
    s = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", s, flags=re.DOTALL)
    s = re.sub(r"<li[^>]*>", "- ", s)
    s = re.sub(r"<(strong|b)>(.*?)</\1>", r"**\2**", s, flags=re.DOTALL)
    s = re.sub(r"<(em|i)>(.*?)</\1>", r"*\2*", s, flags=re.DOTALL)
    s = re.sub(r"<code[^>]*>(.*?)</code>", lambda m: "`" + html.unescape(m.group(1)) + "`", s, flags=re.DOTALL)
    s = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r"[\2](\1)", s, flags=re.DOTALL)
    s = re.sub(r"</p>|</li>|</ul>|</ol>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def extract_section(body_md: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", body_md, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def render_entry(e: dict, fmt: str) -> str:
    head = (
        f"## {e['title']}  `{e['id']}`\n"
        f"*category: {e['category']} · severity: {e['severity']} · "
        f"detection: {e['detection']} · trend as of last review: "
        f"{e.get('last_reviewed', '?')}*\n"
        f"{e['url']}\n\n{e['summary'].strip()}"
    )
    if fmt == "brief":
        return head

    body_md = html_to_markdown(e.get("body_html", "")) if e.get("body_html") else e.get("body_text", "")
    if fmt == "full":
        sources = "\n".join(f"- [{s['title']}]({s['url']})" for s in e.get("sources", []))
        return f"{head}\n\n{body_md}\n\n### Sources\n{sources}"

    # standard: summary + detection + mitigation
    parts = [head]
    for section in ("Detection", "Mitigation"):
        text = extract_section(body_md, section)
        if text:
            parts.append(f"### {section}\n{text}")
    return "\n\n".join(parts)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sel = p.add_mutually_exclusive_group()
    sel.add_argument("--categories", help="comma-separated category names")
    sel.add_argument("--ids", help="comma-separated entry ids")
    sel.add_argument("--all", action="store_true", help="all entries")
    sel.add_argument("--list", action="store_true", help="one line per entry")
    p.add_argument("--format", choices=["brief", "standard", "full"], default="standard")
    p.add_argument("--url", default=DEFAULT_URL, help="atlas.json URL or local path")
    p.add_argument("--no-cache", action="store_true", help="force a live fetch")
    args = p.parse_args()

    atlas, source = load_atlas(args.url, args.no_cache)
    entries = atlas["entries"]

    if args.list:
        print(f"# Blind Spot Atlas — {len(entries)} entries (source: {source})")
        for e in entries:
            print(f"{e['id']:24} {e['category']:22} severity={e['severity']:6} {e['summary'].strip()[:90]}")
        return 0

    if args.categories:
        wanted = {c.strip() for c in args.categories.split(",")}
        known = set(atlas.get("categories", {}))
        unknown = wanted - known
        if unknown and known:
            print(f"warning: unknown categories {sorted(unknown)}; known: {sorted(known)}", file=sys.stderr)
        entries = [e for e in entries if e["category"] in wanted]
    elif args.ids:
        wanted_ids = [i.strip() for i in args.ids.split(",")]
        by_id = {e["id"]: e for e in entries}
        missing = [i for i in wanted_ids if i not in by_id]
        if missing:
            print(f"warning: no entries for ids {missing}", file=sys.stderr)
        entries = [by_id[i] for i in wanted_ids if i in by_id]
    # --all or no selector: keep everything

    if "SNAPSHOT" in source or "STALE" in source:
        print(f"warning: not using the live atlas — source: {source}", file=sys.stderr)

    print(f"# Blind Spot Atlas — {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} (source: {source})\n")
    print("\n\n---\n\n".join(render_entry(e, args.format) for e in entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
