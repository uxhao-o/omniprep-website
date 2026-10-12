# -*- coding: utf-8 -*-
"""Build a lightweight client-side search index from dist HTML pages."""
import json, re, html, pathlib

DIST = pathlib.Path(__file__).parent / "dist"

def strip_html(raw: str) -> str:
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()

def title_of(raw: str) -> str:
    m = re.search(r"<title>(.*?)</title>", raw, re.S)
    return html.unescape(m.group(1)).strip() if m else ""

def collect(base: pathlib.Path, prefix: str, lang: str):
    items = []
    for p in sorted(base.rglob("index.html")):
        rel = p.parent.relative_to(base)
        url = prefix + "/" if rel == pathlib.Path(".") else f"{prefix}/{rel.as_posix()}/"
        raw = p.read_text(encoding="utf-8")
        items.append({
            "url": url,
            "title": title_of(raw) or url,
            "text": strip_html(raw)[:4000],
            "lang": lang,
        })
    return items

items = []
if (DIST / "index.html").exists():
    items += collect(DIST, "", "en")
zh_dir = DIST / "zh"
if zh_dir.exists():
    items += collect(zh_dir, "/zh", "zh")

out = DIST / "search-index.json"
out.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
print(f"search-index.json: {len(items)} pages")
