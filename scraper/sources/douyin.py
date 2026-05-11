from __future__ import annotations

from .base import session

KEY = "douyin"
LABEL = "抖音热搜"
KIND = "single"

URL = "https://aweme.snssdk.com/aweme/v1/hot/search/list/"
QUERIES = {
    "device_platform": "android",
    "version_name": "13.2.0",
    "version_code": "130200",
    "aid": "1128",
}


def fetch() -> list[dict]:
    s = session(headers={"user-agent": "okhttp3"})
    resp = s.get(URL, params=QUERIES, timeout=30)
    resp.raise_for_status()
    data = resp.json() or {}
    word_list = (data.get("data") or {}).get("word_list") or []
    items: list[dict] = []
    for rank, w in enumerate(word_list, 1):
        word = w.get("word") or ""
        hot = w.get("hot_value") or 0
        items.append({
            "rank": rank,
            "title": word,
            "url": f"https://www.douyin.com/search/{word}",
            "metric": f"{hot:,}" if isinstance(hot, int) else str(hot),
            "metric_value": hot if isinstance(hot, int) else 0,
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
