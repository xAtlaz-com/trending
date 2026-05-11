from __future__ import annotations

import json

from .base import session

KEY = "toutiao"
LABEL = "头条热榜"
KIND = "single"

URL = "https://i-lq.snssdk.com/api/feed/hotboard_online/v1/"


def fetch() -> list[dict]:
    s = session()
    resp = s.get(URL, params={"category": "hotboard_online", "count": "50"}, timeout=30)
    resp.raise_for_status()
    items: list[dict] = []
    for rank, raw in enumerate((resp.json() or {}).get("data") or [], 1):
        content = raw
        if isinstance(raw, dict) and isinstance(raw.get("content"), str):
            try:
                content = json.loads(raw["content"])
            except Exception:
                content = {}
        title = content.get("title") or content.get("Title")
        url = content.get("share_url") or content.get("url") or content.get("display_url")
        hot = content.get("hot_value") or content.get("HotValue") or content.get("read_count") or 0
        items.append({
            "rank": rank,
            "title": title or "",
            "url": url or "",
            "metric": f"{int(hot):,}" if str(hot).isdigit() else str(hot),
            "metric_value": int(hot) if str(hot).isdigit() else 0,
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
