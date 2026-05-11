from __future__ import annotations

from .base import session

KEY = "bilibili"
LABEL = "Bilibili 热门"
KIND = "single"

URL = "https://api.bilibili.com/x/web-interface/popular"


def fetch() -> list[dict]:
    s = session(headers={"Referer": "https://www.bilibili.com/"})
    resp = s.get(URL, params={"ps": "50", "pn": "1"}, timeout=30)
    resp.raise_for_status()
    raw = ((resp.json() or {}).get("data") or {}).get("list") or []
    items: list[dict] = []
    for rank, v in enumerate(raw, 1):
        stat = v.get("stat") or {}
        bvid = v.get("bvid") or ""
        items.append({
            "rank": rank,
            "title": v.get("title") or "",
            "url": f"https://www.bilibili.com/video/{bvid}" if bvid else v.get("short_link_v2") or "",
            "description": (v.get("desc") or "")[:300],
            "image": v.get("pic"),
            "channel": (v.get("owner") or {}).get("name"),
            "metric": f"▶ {stat.get('view', 0):,}",
            "metric_value": stat.get("view", 0),
            "extra": {
                "likes": stat.get("like"),
                "danmaku": stat.get("danmaku"),
                "reason": (v.get("rcmd_reason") or {}).get("content"),
                "duration": v.get("duration"),
            },
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
