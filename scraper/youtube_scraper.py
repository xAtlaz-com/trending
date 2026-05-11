"""
Fetch YouTube `chart=mostPopular` per country.

Writes to:
  data/raw/<CC>.json                                   — always overwritten (latest raw, drives latest.json + RSS)
  data/archive/<YY.MM.DD>/<HH>/<CC>.json               — only when current UTC hour ∈ ARCHIVE_HOURS (default 00,12)
                                                          and that slot hasn't been written yet today
"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
ARCHIVE = ROOT / "data" / "archive"

API_KEY = os.environ.get("YOUTUBE_DATA_API_KEY")
if not API_KEY:
    sys.stderr.write("ERROR: YOUTUBE_DATA_API_KEY env var is missing\n")
    sys.exit(1)

COUNTRIES = [c.strip() for c in os.environ.get("COUNTRIES", "US,JP,KR,GB,IN,HK,TW").split(",") if c.strip()]
ARCHIVE_HOURS = {int(h) for h in os.environ.get("ARCHIVE_HOURS", "0,12").split(",") if h.strip()}
PARTS = "id,snippet,contentDetails,statistics,player,topicDetails"


def fetch_country(cc: str) -> list[dict]:
    items: list[dict] = []
    page_token = None
    while True:
        params = {
            "part": PARTS,
            "chart": "mostPopular",
            "regionCode": cc,
            "maxResults": 50,
            "key": API_KEY,
        }
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get("https://www.googleapis.com/youtube/v3/videos", params=params, timeout=30)
        if resp.status_code == 429:
            sys.stderr.write(f"[{cc}] 429 rate limited, aborting\n")
            sys.exit(2)
        if resp.status_code != 200:
            sys.stderr.write(f"[{cc}] HTTP {resp.status_code}: {resp.text[:300]}\n")
            return items
        data = resp.json()
        items.extend(data.get("items", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return items


def write_raw(cc: str, items: list[dict]) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"{cc}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return path


def maybe_archive(cc: str, items: list[dict], now: time.struct_time) -> Path | None:
    if now.tm_hour not in ARCHIVE_HOURS:
        return None
    day = time.strftime("%y.%m.%d", now)
    slot_folder = ARCHIVE / day / f"{now.tm_hour:02d}"
    path = slot_folder / f"{cc}.json"
    # Slot is "claimed" once the file exists — robust to cron drift / retries.
    if path.exists():
        return None
    slot_folder.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return path


def main() -> None:
    now = time.gmtime()
    for cc in COUNTRIES:
        print(f"[{cc}] fetching...", flush=True)
        items = fetch_country(cc)
        if not items:
            print(f"[{cc}] no items, skipping", flush=True)
            continue
        raw_path = write_raw(cc, items)
        archived = maybe_archive(cc, items, now)
        msg = f"[{cc}] {len(items)} items -> {raw_path.relative_to(ROOT)}"
        if archived:
            msg += f" (archived to {archived.relative_to(ROOT)})"
        print(msg, flush=True)


if __name__ == "__main__":
    main()
