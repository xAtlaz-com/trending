"""
Generate sitemap.xml at repo root listing the homepage + every archive
directory level. Run after generate_archive_index.py.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "data" / "archive"
BASE = "https://trending.subdownload.com"


def url_entry(loc: str, lastmod: str | None = None, changefreq: str | None = None, priority: str | None = None) -> str:
    parts = [f"  <url>", f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{lastmod}</lastmod>")
    if changefreq:
        parts.append(f"    <changefreq>{changefreq}</changefreq>")
    if priority:
        parts.append(f"    <priority>{priority}</priority>")
    parts.append("  </url>")
    return "\n".join(parts)


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    entries: list[str] = []

    # Homepage — highest priority, refreshes constantly
    entries.append(url_entry(f"{BASE}/", lastmod=now, changefreq="always", priority="1.0"))

    # Archive root
    if ARCHIVE.exists():
        entries.append(url_entry(f"{BASE}/data/archive/", lastmod=now, changefreq="hourly", priority="0.8"))

        days = sorted((p for p in ARCHIVE.iterdir() if p.is_dir()), key=lambda p: p.name, reverse=True)
        for day in days:
            day_mtime = datetime.fromtimestamp(day.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            entries.append(url_entry(f"{BASE}/data/archive/{day.name}/", lastmod=day_mtime, changefreq="daily", priority="0.6"))
            for hour in sorted((p for p in day.iterdir() if p.is_dir()), key=lambda p: p.name):
                hour_mtime = datetime.fromtimestamp(hour.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
                entries.append(url_entry(f"{BASE}/data/archive/{day.name}/{hour.name}/", lastmod=hour_mtime, changefreq="never", priority="0.4"))

    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml.extend(entries)
    xml.append("</urlset>")

    (ROOT / "sitemap.xml").write_text("\n".join(xml), encoding="utf-8")
    print(f"sitemap: {len(entries)} URLs")


if __name__ == "__main__":
    main()
