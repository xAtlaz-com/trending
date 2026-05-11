from __future__ import annotations

import re
import sys
from urllib.parse import quote

from bs4 import BeautifulSoup

from .base import session

KEY = "instagram"
LABEL = "Instagram Hashtags"
KIND = "single"

URL = "https://top-hashtags.com/instagram/"


def fetch() -> list[dict]:
    s = session(headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    resp = s.get(URL, timeout=30)
    if resp.status_code != 200:
        print(f"[{KEY}] HTTP {resp.status_code}", file=sys.stderr)
        return []
    soup = BeautifulSoup(resp.text, "html.parser")

    seen = set()
    items: list[dict] = []
    # Try several selectors — top-hashtags.com markup has changed historically.
    selectors = [
        'a[href*="/hashtag/"]',
        'div.tag-box a',
        'table tr a',
        '.text-box',
    ]
    for sel in selectors:
        found = soup.select(sel)
        if not found:
            continue
        print(f"[{KEY}] matched selector {sel!r}: {len(found)} elements", file=sys.stderr)
        for el in found:
            text = el.get_text(strip=True)
            if not text:
                continue
            tag = text.lstrip("#").strip()
            if not tag or " " in tag or len(tag) > 60 or tag in seen:
                continue
            # filter obvious nav links
            if re.search(r"[A-Z]{2,}|http|\.|/", tag):
                continue
            seen.add(tag)
            items.append({
                "rank": len(items) + 1,
                "title": f"#{tag}",
                "url": f"https://www.instagram.com/explore/tags/{quote(tag)}/",
                "extra": {"hashtag": tag, "source_url": f"https://top-hashtags.com/hashtag/{tag}"},
            })
            if len(items) >= 50:
                break
        if items:
            break

    if not items:
        print(f"[{KEY}] no items extracted from {len(resp.text)} bytes", file=sys.stderr)
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
