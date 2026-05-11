from __future__ import annotations

from .base import session

KEY = "reddit"
LABEL = "Reddit Popular"
KIND = "single"

URL = "https://www.reddit.com/r/popular.json"


def fetch() -> list[dict]:
    s = session(headers={"User-Agent": "web:xatlaz-trending:1.0 (by /u/xatlaz)"})
    resp = s.get(URL, params={"limit": "50"}, timeout=30)
    resp.raise_for_status()
    children = ((resp.json() or {}).get("data") or {}).get("children") or []
    items: list[dict] = []
    for rank, c in enumerate(children, 1):
        d = c.get("data") or {}
        # skip stickied / promoted
        if d.get("stickied") or d.get("promoted"):
            continue
        thumb = d.get("thumbnail")
        if thumb in {"self", "default", "nsfw", "spoiler", "image", ""}:
            thumb = None
        # prefer preview image if available
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
                "is_video": d.get("is_video"),
            },
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
