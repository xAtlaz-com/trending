from __future__ import annotations

import sys

from . import _aggregator
from .base import session

KEY = "zhihu"
LABEL = "知乎热榜"
KIND = "single"

URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"


def _fetch_direct() -> list[dict]:
    s = session(headers={"x-api-version": "3.0.76"})
    resp = s.get(URL, timeout=30)
    if resp.status_code != 200:
        return []
    items: list[dict] = []
    for rank, it in enumerate((resp.json() or {}).get("data") or [], 1):
        target = it.get("target") or {}
        items.append({
            "rank": rank,
            "title": (target.get("title_area") or {}).get("text", "") or "",
            "url": (target.get("link") or {}).get("url") or "",
            "description": ((target.get("excerpt_area") or {}).get("text", "") or "")[:300],
            "image": (target.get("image_area") or {}).get("url"),
            "metric": (target.get("metrics_area") or {}).get("text", "") or "",
        })
    return items


def fetch() -> list[dict]:
    try:
        items = _fetch_direct()
        if items:
            print(f"[{KEY}] direct OK, {len(items)} items", file=sys.stderr)
            return items
        print(f"[{KEY}] direct returned 0, falling back to aggregator", file=sys.stderr)
    except Exception as e:
        print(f"[{KEY}] direct failed: {e}, falling back to aggregator", file=sys.stderr)
    return _aggregator.fetch_hot("zhihu")


def normalize(items: list[dict]) -> list[dict]:
    return items
