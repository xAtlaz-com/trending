from __future__ import annotations

from bs4 import BeautifulSoup

from .base import session

KEY = "github"
LABEL = "GitHub Trending"
KIND = "single"


def fetch() -> list[dict]:
    s = session()
    resp = s.get("https://github.com/trending", params={"since": "daily"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items: list[dict] = []
    for rank, article in enumerate(soup.select("main article.Box-row"), 1):
        a = article.select_one("h2.h3 a") or article.select_one("h1.h3 a")
        if not a:
            continue
        href = " ".join(a.get_text().split())
        url = "https://github.com/" + href.replace(" ", "")
        desc_el = article.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""
        lang_el = article.select_one('[itemprop="programmingLanguage"]')
        language = lang_el.get_text(strip=True) if lang_el else None
        stars_el = article.select_one('a[href$="/stargazers"]')
        forks_el = article.select_one('a[href$="/forks"]')
        stars = stars_el.get_text(strip=True) if stars_el else "0"
        forks = forks_el.get_text(strip=True) if forks_el else "0"
        recent_el = article.select_one("span.d-inline-block.float-sm-right")
        recent = recent_el.get_text(strip=True) if recent_el else ""
        items.append({
            "rank": rank,
            "title": href,
            "url": url,
            "description": description,
            "metric": f"★ {stars}",
            "extra": {
                "language": language,
                "stars": stars,
                "forks": forks,
                "stars_today": recent,
            },
        })
    return items


def normalize(items: list[dict]) -> list[dict]:
    return items
