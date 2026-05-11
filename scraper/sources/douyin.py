from __future__ import annotations

from .base import session

KEY = "douyin"
LABEL = "抖音热搜"
KIND = "single"

URL = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
PARAMS = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "detail_list": "1",
}


def fetch() -> list[dict]:
    s = session(headers={
        "Referer": "https://www.douyin.com/hot",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
    })
    resp = s.get(URL, params=PARAMS, timeout=30)
    resp.raise_for_status()
    word_list = ((resp.json() or {}).get("data") or {}).get("word_list") or []
    items: list[dict] = []
    for rank, w in enumerate(word_list, 1):
        word = w.get("word") or ""
        if not word:
            continue
        hot = w.get("hot_value") or 0
        sentence_id = w.get("sentence_id")
        items.append({
            "rank": rank,
            "title": word,
            "url": f"https://www.douyin.com/hot/{sentence_id}" if sentence_id else f"https://www.douyin.com/search/{word}",
            "metric": f"🔥 {hot:,}" if isinstance(hot, int) else str(hot),
            "metric_value": hot if isinstance(hot, int) else 0,
            "extra": {
                "event_time": w.get("event_time"),
                "label": w.get("label"),
                "discuss_video_count": w.get("discuss_video_count"),
            },
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
