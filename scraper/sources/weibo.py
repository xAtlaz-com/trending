from __future__ import annotations

import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from . import _aggregator
from .base import session

KEY = "weibo"
LABEL = "微博热搜"
KIND = "single"

URL = "https://s.weibo.com/top/summary?cate=realtimehot"


def _fetch_direct() -> list[dict]:
    s = session()
    resp = s.get(URL, timeout=30, allow_redirects=False)
    if resp.status_code != 200:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    items: list[dict] = []
    rows = soup.select("table tbody tr")
    rank = 0
    for tr in rows:
        td = tr.select_one("td.td-02")
        if not td:
            continue
        a = td.select_one("a")
        if not a:
            continue
        rank += 1
        href = a.get("href", "")
        url = urljoin("https://s.weibo.com", href)
        title = a.get_text(strip=True)
        span = td.select_one("span")
        hot = span.get_text(strip=True) if span else ""
        items.append({"rank": rank, "title": title, "url": url, "metric": hot})
    return items


def fetch() -> list[dict]:
    try:
        items = _fetch_direct()
        if items:
            print(f"[{KEY}] direct OK, {len(items)} items", file=sys.stderr)
            return items
        print(f"[{KEY}] direct returned 0, falling back to aggregator", file=sys.stderr)
    except Exception as e:
        print(f"[{KEY}] direct failed: {e}, falling back to aggregator", file=sys.stderr)
    return _aggregator.fetch_hot("weibo")


def normalize(items: list[dict]) -> list[dict]:
    return items
