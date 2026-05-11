from __future__ import annotations

import re
import sys
from html import unescape
from xml.etree import ElementTree as ET

from .base import session

KEY = "reddit"
LABEL = "Reddit Popular"
KIND = "single"

# Reddit aggressively rate-limits cloud IPs (Azure/AWS) on the .json endpoint.
# RSS is less protected and is officially supported.
RSS_URL = "https://www.reddit.com/r/popular/.rss"
JSON_URL = "https://www.reddit.com/r/popular.json"

NS = {"atom": "http://www.w3.org/2005/Atom"}
IMG_RE = re.compile(r'<img[^>]+src="([^"]+)"', re.I)
HTML_RE = re.compile(r"<[^>]+>")


def _from_json() -> list[dict]:
    s = session(headers={"User-Agent": "web:xatlaz-trending:1.0 (by /u/xatlaz)"})
    resp = s.get(JSON_URL, params={"limit": "50"}, timeout=30)
    if resp.status_code != 200:
        print(f"[{KEY}] json HTTP {resp.status_code}", file=sys.stderr)
        return []
    children = ((resp.json() or {}).get("data") or {}).get("children") or []
    items: list[dict] = []
    for rank, c in enumerate(children, 1):
        d = c.get("data") or {}
        if d.get("stickied") or d.get("promoted"):
            continue
        thumb = d.get("thumbnail")
        if thumb in {"self", "default", "nsfw", "spoiler", "image", ""}:
            thumb = None
        preview = (d.get("preview") or {}).get("images") or []
        if preview:
            src = (preview[0] or {}).get("source") or {}
            if src.get("url"):
                thumb = src["url"].replace("&amp;", "&")
        permalink = d.get("permalink") or ""
        ups = d.get("ups") or d.get("score") or 0
        items.append({
            "rank": rank,
            "title": d.get("title") or "",
            "url": f"https://www.reddit.com{permalink}" if permalink else (d.get("url") or ""),
            "description": (d.get("selftext") or "")[:300],
            "image": thumb,
            "metric": f"↑{ups:,} · 💬{d.get('num_comments', 0):,}",
            "metric_value": ups,
            "extra": {
                "subreddit": d.get("subreddit_name_prefixed"),
                "author": d.get("author"),
                "domain": d.get("domain"),
            },
        })
    return items


def _from_rss() -> list[dict]:
    s = session(headers={"User-Agent": "web:xatlaz-trending:1.0 (by /u/xatlaz)"})
    resp = s.get(RSS_URL, timeout=30)
    if resp.status_code != 200:
        print(f"[{KEY}] rss HTTP {resp.status_code}", file=sys.stderr)
        return []
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        print(f"[{KEY}] rss parse: {e}", file=sys.stderr)
        return []
    items: list[dict] = []
    for rank, entry in enumerate(root.findall("atom:entry", NS), 1):
        title = (entry.findtext("atom:title", default="", namespaces=NS) or "").strip()
        link_el = entry.find("atom:link", NS)
        href = link_el.get("href") if link_el is not None else ""
        content_raw = entry.findtext("atom:content", default="", namespaces=NS) or ""
        content_html = unescape(content_raw)
        img_match = IMG_RE.search(content_html)
        image = img_match.group(1) if img_match else None
        # subreddit from category term
        cat_el = entry.find("atom:category", NS)
        subreddit = cat_el.get("label") if cat_el is not None else (cat_el.get("term") if cat_el is not None else None)
        author = entry.findtext("atom:author/atom:name", default="", namespaces=NS) or None
        items.append({
            "rank": rank,
            "title": title,
            "url": href,
            "image": image,
            "extra": {"subreddit": subreddit, "author": author},
        })
        if rank >= 50:
            break
    return items


def fetch() -> list[dict]:
    try:
        items = _from_json()
        if items:
            return items
    except Exception as e:
        print(f"[{KEY}] json path failed: {e}", file=sys.stderr)
    return _from_rss()


def normalize(items: list[dict]) -> list[dict]:
    return items
