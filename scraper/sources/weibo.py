from __future__ import annotations

from urllib.parse import quote

from .base import session

KEY = "weibo"
LABEL = "微博热搜"
KIND = "single"

URL = "https://weibo.com/ajax/side/hotSearch"


def fetch() -> list[dict]:
    s = session(headers={
        "Referer": "https://weibo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
    })
    resp = s.get(URL, timeout=30)
    resp.raise_for_status()
    realtime = ((resp.json() or {}).get("data") or {}).get("realtime") or []
    items: list[dict] = []
    for rank, v in enumerate(realtime, 1):
        word = v.get("word") or v.get("word_scheme") or f"热搜{rank}"
        items.append({
            "rank": rank,
            "title": word,
            "url": f"https://s.weibo.com/weibo?q={quote(word)}",
            "description": v.get("word_scheme") or "",
            "metric": f"{v.get('num'):,}" if isinstance(v.get("num"), int) else (v.get("note") or ""),
            "metric_value": v.get("num") if isinstance(v.get("num"), int) else 0,
            "extra": {"label_name": v.get("label_name"), "category": v.get("category")},
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
