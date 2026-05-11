"""
Read data/raw/ produced by scrape_all.py and produce:
  data/latest.json                     — combined snapshot (all sources)
  data/latest/<key>.json               — single-source snapshot
  data/latest/<key>/<CC>.json          — multi-country sub-snapshot (youtube)
  data/feed.xml                        — combined RSS 2.0
  data/feeds/<key>.xml                 — per-source RSS 2.0
  data/feeds/<key>-<CC>.xml            — multi-country sub-feed
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from importlib import import_module
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data"

sys.path.insert(0, str(Path(__file__).resolve().parent))

SITE_TITLE = "Trending Pages"
SITE_URL = "https://xatlaz-com.github.io/trending/"

SOURCES = [
    s.strip() for s in os.environ.get(
        "SOURCES", "youtube,github,v2ex,weibo,zhihu,douyin,toutiao,reddit,bilibili"
    ).split(",") if s.strip()
]
COUNTRY_ORDER = [c.strip() for c in os.environ.get("COUNTRIES", "GB,US,JP,KR,IN,HK,TW").split(",") if c.strip()]


def ordered_countries(found):
    known = [c for c in COUNTRY_ORDER if c in found]
    extra = sorted(c for c in found if c not in COUNTRY_ORDER)
    return known + extra


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def rss(items, title, link, description, updated):
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        f"<title>{escape(title)}</title>",
        f"<link>{escape(link)}</link>",
        f"<description>{escape(description)}</description>",
        f"<lastBuildDate>{format_datetime(updated)}</lastBuildDate>",
        f'<atom:link href="{escape(link)}" rel="self" type="application/rss+xml" />',
    ]
    for it in items:
        url = it.get("url") or ""
        title_t = it.get("title") or ""
        guid = url or title_t
        if not guid:
            continue
        try:
            pub = it.get("published_at")
            published = datetime.fromisoformat(pub.replace("Z", "+00:00")) if pub else updated
        except Exception:
            published = updated
        desc_bits = []
        if it.get("rank"):
            desc_bits.append(f"#{it['rank']}")
        if it.get("metric"):
            desc_bits.append(str(it["metric"]))
        if it.get("channel"):
            desc_bits.append(f"@{it['channel']}")
        if it.get("description"):
            desc_bits.append(str(it["description"])[:280])
        parts += [
            "<item>",
            f"<title>{escape(title_t)}</title>",
            f"<link>{escape(url)}</link>",
            f'<guid isPermaLink="false">{escape(guid)}</guid>',
            f"<pubDate>{format_datetime(published)}</pubDate>",
            f"<description>{escape(' | '.join(desc_bits))}</description>",
            "</item>",
        ]
    parts += ["</channel>", "</rss>"]
    return "\n".join(parts)


def process_source(key, updated):
    """Returns (meta_dict, data_for_combined) or None if nothing to emit."""
    try:
        mod = import_module(f"sources.{key}")
    except Exception as e:
        print(f"[{key}] import failed: {e}")
        return None
    kind = getattr(mod, "KIND", "single")
    label = getattr(mod, "LABEL", key)

    if kind == "multi-country":
        source_dir = RAW / key
        if not source_dir.exists():
            return None
        found = sorted(p.stem for p in source_dir.glob("*.json"))
        if not found:
            return None
        countries = ordered_countries(found)
        per_country = {}
        for cc in countries:
            raw_items = json.loads((source_dir / f"{cc}.json").read_text(encoding="utf-8"))
            items = mod.normalize(raw_items)
            per_country[cc] = items
            write_json(DATA / "latest" / key / f"{cc}.json", {
                "source": key, "country": cc,
                "updated_at": updated.isoformat(),
                "count": len(items), "items": items,
            })
            write_text(DATA / "feeds" / f"{key}-{cc}.xml",
                rss(items,
                    title=f"{SITE_TITLE} — {label} {cc}",
                    link=f"{SITE_URL}#{key}/{cc}",
                    description=f"{label} trending for {cc}, refreshed every 30 minutes.",
                    updated=updated))
        meta = {"key": key, "label": label, "kind": kind, "countries": countries}
        return meta, per_country
    else:
        raw_file = RAW / f"{key}.json"
        if not raw_file.exists():
            return None
        raw_items = json.loads(raw_file.read_text(encoding="utf-8"))
        items = mod.normalize(raw_items)
        if not items:
            return None
        write_json(DATA / "latest" / f"{key}.json", {
            "source": key,
            "updated_at": updated.isoformat(),
            "count": len(items), "items": items,
        })
        write_text(DATA / "feeds" / f"{key}.xml",
            rss(items,
                title=f"{SITE_TITLE} — {label}",
                link=f"{SITE_URL}#{key}",
                description=f"{label}, refreshed every 30 minutes.",
                updated=updated))
        meta = {"key": key, "label": label, "kind": kind}
        return meta, items


def main() -> None:
    updated = datetime.now(timezone.utc).replace(microsecond=0)
    sources_meta = []
    combined_data = {}
    all_items = []

    for key in SOURCES:
        result = process_source(key, updated)
        if result is None:
            print(f"[{key}] no data, skipping")
            continue
        meta, data = result
        sources_meta.append(meta)
        combined_data[key] = data
        if meta["kind"] == "multi-country":
            for cc, items in data.items():
                for it in items:
                    all_items.append({**it, "source": key, "country": cc})
        else:
            for it in data:
                all_items.append({**it, "source": key})

    if not sources_meta:
        print("nothing produced")
        return

    write_json(DATA / "latest.json", {
        "updated_at": updated.isoformat(),
        "sources": sources_meta,
        "data": combined_data,
    })

    write_text(DATA / "feed.xml",
        rss(all_items,
            title=f"{SITE_TITLE} — All sources",
            link=SITE_URL,
            description="Trending across YouTube, GitHub, V2EX, 微博, 知乎, 抖音, 头条 — refreshed every 30 minutes.",
            updated=updated))

    print(f"generated {len(sources_meta)} sources, {len(all_items)} total items")


if __name__ == "__main__":
    main()
