"""
Fallback via DailyHot aggregator (github.com/imsyy/DailyHot).
Public instance at api-hot.imsyy.top. Used when a source's direct endpoint
needs cookies/auth/geo we can't satisfy from GitHub Actions runners.
"""
from __future__ import annotations

from .base import session

BASE = "https://api-hot.imsyy.top"


def fetch_hot(name: str) -> list[dict]:
    s = session()
    resp = s.get(f"{BASE}/{name}", params={"cache": "false"}, timeout=30)
    resp.raise_for_status()
    payload = resp.json() or {}
    data = payload.get("data") or []
    items: list[dict] = []
    for rank, it in enumerate(data, 1):
        url = it.get("mobileUrl") or it.get("url") or ""
        hot = it.get("hot")
        items.append({
            "rank": rank,
            "title": (it.get("title") or "").strip(),
            "url": url,
            "description": (it.get("desc") or "").strip()[:300],
            "image": it.get("cover") or None,
            "metric": str(hot) if hot is not None else "",
            "metric_value": int(hot) if isinstance(hot, (int, float)) else 0,
            "extra": {"author": it.get("author")} if it.get("author") else {},
        })
    return items
