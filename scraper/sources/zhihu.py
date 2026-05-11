from __future__ import annotations

from .base import session

KEY = "zhihu"
LABEL = "知乎热榜"
KIND = "single"

URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"


def fetch() -> list[dict]:
    s = session(headers={"x-api-version": "3.0.76"})
    resp = s.get(URL, timeout=30)
    resp.raise_for_status()
    items: list[dict] = []
    for rank, it in enumerate((resp.json() or {}).get("data") or [], 1):
        target = it.get("target") or {}
        title = (target.get("title_area") or {}).get("text", "") or ""
        url = (target.get("link") or {}).get("url") or ""
        excerpt = (target.get("excerpt_area") or {}).get("text", "") or ""
        metric = (target.get("metrics_area") or {}).get("text", "") or ""
        image = (target.get("image_area") or {}).get("url")
        items.append({
            "rank": rank,
            "title": title,
            "url": url,
            "description": excerpt[:300],
            "image": image,
            "metric": metric,
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
