from __future__ import annotations

import json
import re
import sys

from bs4 import BeautifulSoup

from .base import session

KEY = "tiktok"
LABEL = "TikTok Trending"
KIND = "single"

# Creative Center's SSR HTML embeds initial props as JSON — no auth/signing needed.
URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"


def fetch() -> list[dict]:
    s = session(headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    resp = s.get(URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # SSR initial data is in a script tag like <script id="__APP_PROPS__">{...}</script>
    # or window.__APP_PROPS__ = {...}; — try both.
    items: list[dict] = []
    payload = None
    for script in soup.find_all("script"):
        text = script.string or ""
        if "popularTrendList" in text or "hashtag_name" in text:
            m = re.search(r"\{[^{}]*\"hashtag_name\".*", text)
            if m:
                # Walk balanced braces to extract the JSON value.
                start = m.start()
                stack = 0
                end = None
                for i, ch in enumerate(text[start:], start):
                    if ch == "{":
                        stack += 1
                    elif ch == "}":
                        stack -= 1
                        if stack == 0:
                            end = i + 1
                            break
                if end:
                    try:
                        payload = json.loads(text[start:end])
                    except Exception:
                        pass
                break
    if not payload:
        print(f"[{KEY}] no SSR payload found in {len(resp.text)} bytes; "
              f"has __APP_PROPS__={'__APP_PROPS__' in resp.text} "
              f"has hashtag_name={'hashtag_name' in resp.text}", file=sys.stderr)
        return []

    # Find any list with hashtag entries.
    def walk(obj):
        if isinstance(obj, dict):
            if obj.get("hashtag_name"):
                yield obj
            for v in obj.values():
                yield from walk(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from walk(v)

    seen = set()
    for entry in walk(payload):
        name = entry.get("hashtag_name")
        if not name or name in seen:
            continue
        seen.add(name)
        items.append({
            "rank": entry.get("rank") or len(items) + 1,
            "title": f"#{name}",
            "url": f"https://www.tiktok.com/tag/{name}",
            "metric": f"📹 {entry.get('publish_cnt', 0):,}" if entry.get("publish_cnt") else "",
            "metric_value": entry.get("publish_cnt") or 0,
            "extra": {
                "video_views": entry.get("video_views"),
                "country_code": entry.get("country_code"),
                "industry": entry.get("industry"),
            },
        })
    items.sort(key=lambda x: x["rank"])
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
