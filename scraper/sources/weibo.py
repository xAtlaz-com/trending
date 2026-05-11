from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import session

KEY = "weibo"
LABEL = "微博热搜"
KIND = "single"

URL = "https://s.weibo.com/top/summary?cate=realtimehot"


def fetch() -> list[dict]:
    s = session()
    resp = s.get(URL, timeout=30)
    resp.raise_for_status()
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
        label_el = tr.select_one("td.td-03 i")
        label = label_el.get_text(strip=True) if label_el else ""
        items.append({
            "rank": rank,
            "title": title,
            "url": url,
            "metric": hot,
            "extra": {"label": label} if label else {},
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
