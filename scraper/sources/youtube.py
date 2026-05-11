from __future__ import annotations

import os
import sys

from .base import session

KEY = "youtube"
LABEL = "YouTube"
KIND = "multi-country"

PARTS = "id,snippet,contentDetails,statistics,player,topicDetails"


def get_countries() -> list[str]:
    return [c.strip() for c in os.environ.get("COUNTRIES", "US,JP,KR,GB,IN,HK,TW").split(",") if c.strip()]


def fetch() -> dict[str, list[dict]]:
    api_key = os.environ.get("YOUTUBE_DATA_API_KEY")
    if not api_key:
        sys.stderr.write("[youtube] missing YOUTUBE_DATA_API_KEY, skipping\n")
        return {}
    s = session()
    out: dict[str, list[dict]] = {}
    for cc in get_countries():
        items: list[dict] = []
        page_token: str | None = None
        while True:
            params = {
                "part": PARTS,
                "chart": "mostPopular",
                "regionCode": cc,
                "maxResults": 50,
                "key": api_key,
            }
            if page_token:
                params["pageToken"] = page_token
            resp = s.get("https://www.googleapis.com/youtube/v3/videos", params=params, timeout=30)
            if resp.status_code != 200:
                sys.stderr.write(f"[youtube/{cc}] HTTP {resp.status_code}: {resp.text[:200]}\n")
                break
            data = resp.json()
            items.extend(data.get("items", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                break
        if items:
            out[cc] = items
    return out


def normalize(items: list[dict]) -> list[dict]:
    out = []
    for rank, item in enumerate(items, 1):
        snip = item.get("snippet") or {}
        stats = item.get("statistics") or {}
        content = item.get("contentDetails") or {}
        thumbs = snip.get("thumbnails") or {}
        thumb = (
            thumbs.get("maxres") or thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}
        ).get("url")
        vid = item.get("id")
        views = int(stats.get("viewCount", 0) or 0)
        out.append({
            "rank": rank,
            "title": snip.get("title"),
            "url": f"https://www.youtube.com/watch?v={vid}" if vid else None,
            "image": thumb,
            "description": (snip.get("description") or "")[:500],
            "metric": f"{views:,} views",
            "metric_value": views,
            "channel": snip.get("channelTitle"),
            "published_at": snip.get("publishedAt"),
            "extra": {
                "id": vid,
                "channel_id": snip.get("channelId"),
                "category_id": snip.get("categoryId"),
                "tags": snip.get("tags") or [],
                "duration": content.get("duration"),
                "likes": int(stats.get("likeCount", 0) or 0),
                "comments": int(stats.get("commentCount", 0) or 0),
            },
        })
    return out
