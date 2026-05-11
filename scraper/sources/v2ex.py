from __future__ import annotations

import re

from .base import session

KEY = "v2ex"
LABEL = "V2EX"
KIND = "single"

_TAG = re.compile(r"<[^>]+>")


def _strip(html: str) -> str:
    return _TAG.sub("", html or "").strip()


def fetch() -> list[dict]:
    s = session()
    resp = s.get("https://www.v2ex.com/api/topics/hot.json", timeout=30)
    resp.raise_for_status()
    items: list[dict] = []
    for rank, t in enumerate(resp.json() or [], 1):
        items.append({
            "rank": rank,
            "title": t.get("title"),
            "url": t.get("url"),
            "description": _strip(t.get("content_rendered") or "")[:300],
            "metric": f"{t.get('replies', 0)} 回复",
            "metric_value": t.get("replies", 0),
            "extra": {
                "node": (t.get("node") or {}).get("title"),
                "node_name": (t.get("node") or {}).get("name"),
                "author": (t.get("member") or {}).get("username"),
                "last_touched": t.get("last_touched"),
            },
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
