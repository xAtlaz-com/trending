from __future__ import annotations

import sys
from urllib.parse import quote

from bs4 import BeautifulSoup

from .base import session

KEY = "twitter"
LABEL = "X / Twitter Trends"
KIND = "single"

URL = "https://trends24.in/"


def fetch() -> list[dict]:
    s = session(headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    resp = s.get(URL, timeout=30)
    resp.raise_for_status()
    # trends24.in serves UTF-8 but doesn't advertise charset in Content-Type,
    # so requests falls back to ISO-8859-1 and mangles é, 日本語, etc.
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # Page renders multiple time-slot cards; first one is the most recent snapshot.
    card = soup.select_one("ol.trend-card__list") or soup.select_one(".trend-card__list")
    if not card:
        print(f"[{KEY}] no trend-card__list in {len(resp.text)} bytes", file=sys.stderr)
        return []

    items: list[dict] = []
    seen = set()
    for li in card.select("li"):
        a = li.find("a")
        if not a:
            continue
        title = a.get_text(strip=True)
        if not title or title in seen:
            continue
        seen.add(title)
        count_el = li.select_one(".tweet-count")
        count = count_el.get_text(strip=True) if count_el else ""
        items.append({
            "rank": len(items) + 1,
            "title": title,
            "url": a.get("href") or f"https://twitter.com/search?q={quote(title)}",
            "metric": count,
            "extra": {"raw_count": count} if count else {},
        })
        if len(items) >= 50:
            break

    if not items:
        print(f"[{KEY}] card found but no items extracted", file=sys.stderr)
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
