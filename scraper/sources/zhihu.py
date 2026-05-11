from __future__ import annotations

from .base import session

KEY = "zhihu"
LABEL = "知乎热榜"
KIND = "single"

URL = "https://api.zhihu.com/topstory/hot-lists/total?limit=50"


def fetch() -> list[dict]:
    s = session()
    resp = s.get(URL, timeout=30)
    resp.raise_for_status()
    raw_items = (resp.json() or {}).get("data") or []
    items: list[dict] = []
    for rank, v in enumerate(raw_items, 1):
        target = v.get("target") or {}
        children = v.get("children") or []
        thumb = (children[0] or {}).get("thumbnail") if children else None
        url = target.get("url") or ""
        question_id = url.rstrip("/").split("/")[-1] if url else ""
        items.append({
            "rank": rank,
            "title": target.get("title") or "",
            "url": f"https://www.zhihu.com/question/{question_id}" if question_id else url,
            "description": (target.get("excerpt") or "")[:300],
            "image": thumb,
            "metric": v.get("detail_text") or "",
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
