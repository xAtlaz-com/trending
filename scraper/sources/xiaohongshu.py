from __future__ import annotations

import sys

from .base import session

KEY = "xiaohongshu"
LABEL = "小红书热搜"
KIND = "single"

# XHS web-side hot list. Requires no auth for the unsigned public endpoint, but
# headers must match a real browser — Referer + User-Agent + Accept-Language.
URL = "https://edith.xiaohongshu.com/api/sns/web/v1/search/hot_list"


def fetch() -> list[dict]:
    s = session(headers={
        "Referer": "https://www.xiaohongshu.com/",
        "Origin": "https://www.xiaohongshu.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })
    resp = s.get(URL, timeout=30)
    if resp.status_code != 200:
        print(f"[{KEY}] HTTP {resp.status_code}", file=sys.stderr)
        return []
    payload = resp.json() or {}
    if not payload.get("success", True):
        print(f"[{KEY}] api error: {payload.get('msg')}", file=sys.stderr)
        return []
    raw = (payload.get("data") or {}).get("items") or []
    items: list[dict] = []
    for rank, v in enumerate(raw, 1):
        title = v.get("title") or v.get("word") or ""
        if not title:
            continue
        from urllib.parse import quote
        items.append({
            "rank": rank,
            "title": title,
            "url": f"https://www.xiaohongshu.com/search_result?keyword={quote(title)}",
            "metric": f"🔥 {v.get('score', 0):,}" if v.get("score") else "",
            "metric_value": v.get("score") or 0,
            "extra": {"icon": v.get("icon"), "type": v.get("type")},
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
