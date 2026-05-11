from __future__ import annotations

from .base import session

KEY = "toutiao"
LABEL = "头条热榜"
KIND = "single"

URL = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"


def fetch() -> list[dict]:
    s = session()
    resp = s.get(URL, timeout=30)
    resp.raise_for_status()
    raw_items = (resp.json() or {}).get("data") or []
    items: list[dict] = []
    for rank, v in enumerate(raw_items, 1):
        cid = v.get("ClusterIdStr") or ""
        hot = v.get("HotValue") or 0
        hot_int = int(hot) if str(hot).isdigit() else 0
        items.append({
            "rank": rank,
            "title": v.get("Title") or "",
            "url": f"https://www.toutiao.com/trending/{cid}/" if cid else "",
            "image": (v.get("Image") or {}).get("url"),
            "metric": f"{hot_int:,}" if hot_int else "",
            "metric_value": hot_int,
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
