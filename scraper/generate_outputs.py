"""
Read data/raw/<CC>.json (always-fresh, written by the scraper every run) and produce:
  data/latest.json                 — combined snapshot (all countries)
  data/latest/<CC>.json            — per-country snapshot
  data/feed.xml                    — combined RSS 2.0
  data/feeds/<CC>.xml              — per-country RSS 2.0
"""
import json
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data"

SITE_TITLE = "Trending Pages"
SITE_URL = "https://example.github.io/trending/"


def find_raw_per_country() -> dict[str, Path]:
    latest: dict[str, Path] = {}
    if not RAW.exists():
        return latest
    for path in RAW.glob("*.json"):
        m = re.match(r"^([A-Z]{2})\.json$", path.name)
        if m:
            latest[m.group(1)] = path
    return latest


def simplify(items: list[dict], cc: str) -> list[dict]:
    out = []
    for rank, item in enumerate(items, 1):
        snip = item.get("snippet") or {}
        stats = item.get("statistics") or {}
        content = item.get("contentDetails") or {}
        thumbs = (snip.get("thumbnails") or {})
        thumb = (thumbs.get("maxres") or thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}).get("url")
        vid = item.get("id")
        out.append({
            "rank": rank,
            "country": cc,
            "id": vid,
            "title": snip.get("title"),
            "channel": snip.get("channelTitle"),
            "channel_id": snip.get("channelId"),
            "description": (snip.get("description") or "")[:500],
            "published_at": snip.get("publishedAt"),
            "category_id": snip.get("categoryId"),
            "tags": snip.get("tags") or [],
            "duration": content.get("duration"),
            "views": int(stats.get("viewCount", 0) or 0),
            "likes": int(stats.get("likeCount", 0) or 0),
            "comments": int(stats.get("commentCount", 0) or 0),
            "thumbnail": thumb,
            "url": f"https://www.youtube.com/watch?v={vid}" if vid else None,
        })
    return out


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def rss(items: list[dict], title: str, link: str, description: str, updated: datetime) -> str:
    pub = format_datetime(updated)
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        f"<title>{escape(title)}</title>",
        f"<link>{escape(link)}</link>",
        f"<description>{escape(description)}</description>",
        f"<lastBuildDate>{pub}</lastBuildDate>",
        f'<atom:link href="{escape(link)}" rel="self" type="application/rss+xml" />',
    ]
    for it in items:
        if not it.get("id"):
            continue
        try:
            published = datetime.fromisoformat(it["published_at"].replace("Z", "+00:00")) if it.get("published_at") else updated
        except Exception:
            published = updated
        desc_bits = [
            f"#{it['rank']} {it.get('country', '')}",
            f"Channel: {it.get('channel') or '-'}",
            f"Views: {it.get('views', 0):,}",
            (it.get("description") or "")[:280],
        ]
        parts += [
            "<item>",
            f"<title>{escape(it.get('title') or '')}</title>",
            f"<link>{escape(it.get('url') or '')}</link>",
            f"<guid isPermaLink=\"false\">{escape(it['id'])}</guid>",
            f"<pubDate>{format_datetime(published)}</pubDate>",
            f"<description>{escape(' | '.join(desc_bits))}</description>",
            "</item>",
        ]
    parts += ["</channel>", "</rss>"]
    return "\n".join(parts)


def main() -> None:
    raw_files = find_raw_per_country()
    if not raw_files:
        print("no raw files found, nothing to generate")
        return

    updated = datetime.now(timezone.utc).replace(microsecond=0)
    combined: dict[str, list[dict]] = {}
    all_items: list[dict] = []

    for cc, path in sorted(raw_files.items()):
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        items = simplify(raw, cc)
        combined[cc] = items
        all_items.extend(items)

        write_json(DATA / "latest" / f"{cc}.json", {
            "country": cc,
            "updated_at": updated.isoformat(),
            "count": len(items),
            "items": items,
        })

        feed_xml = rss(
            items,
            title=f"{SITE_TITLE} — YouTube {cc}",
            link=f"{SITE_URL}#{cc}",
            description=f"YouTube trending videos for {cc}, refreshed every 30 minutes.",
            updated=updated,
        )
        feed_path = DATA / "feeds" / f"{cc}.xml"
        feed_path.parent.mkdir(parents=True, exist_ok=True)
        feed_path.write_text(feed_xml, encoding="utf-8")

    write_json(DATA / "latest.json", {
        "updated_at": updated.isoformat(),
        "countries": sorted(combined.keys()),
        "data": combined,
    })

    (DATA / "feed.xml").write_text(
        rss(
            all_items,
            title=f"{SITE_TITLE} — YouTube (all regions)",
            link=SITE_URL,
            description="YouTube trending videos across all tracked countries, refreshed every 30 minutes.",
            updated=updated,
        ),
        encoding="utf-8",
    )

    print(f"generated outputs for {len(combined)} countries, total {len(all_items)} items")


if __name__ == "__main__":
    main()
