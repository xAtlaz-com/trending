"""
Orchestrator. Iterates over every source plugin in scraper/sources/, calls fetch(),
writes raw output to data/raw/<key>[.json | /<CC>.json], and on UTC archive hours
also snapshots to data/archive/<YY.MM.DD>/<HH>/<key>[-<CC>].json.

Failures are isolated per source: a broken endpoint does not abort the run.
"""
from __future__ import annotations

import json
import os
import sys
import time
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
ARCHIVE = ROOT / "data" / "archive"

sys.path.insert(0, str(Path(__file__).resolve().parent))

SOURCES = [
    s.strip() for s in os.environ.get(
        "SOURCES", "youtube,github,v2ex,weibo,zhihu,douyin,toutiao,reddit,bilibili,instagram"
    ).split(",") if s.strip()
]
ARCHIVE_HOURS = {int(h) for h in os.environ.get("ARCHIVE_HOURS", "0,12").split(",") if h.strip()}


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _archive_path(key: str, cc: str | None, now: time.struct_time) -> Path:
    day = time.strftime("%y.%m.%d", now)
    hour = f"{now.tm_hour:02d}"
    name = f"{key}-{cc}.json" if cc else f"{key}.json"
    return ARCHIVE / day / hour / name


def main() -> None:
    now = time.gmtime()
    do_archive = now.tm_hour in ARCHIVE_HOURS

    for key in SOURCES:
        try:
            mod = import_module(f"sources.{key}")
        except Exception as e:
            print(f"[{key}] import failed: {e}", flush=True)
            continue
        try:
            print(f"[{key}] fetching...", flush=True)
            raw = mod.fetch()
        except Exception as e:
            print(f"[{key}] fetch failed: {type(e).__name__}: {e}", flush=True)
            continue
        if not raw:
            print(f"[{key}] empty, skipping write", flush=True)
            continue

        kind = getattr(mod, "KIND", "single")
        if kind == "multi-country":
            count = 0
            for cc, items in raw.items():
                _write_json(RAW / key / f"{cc}.json", items)
                if do_archive:
                    p = _archive_path(key, cc, now)
                    if not p.exists():
                        _write_json(p, items)
                count += len(items)
            print(f"[{key}] {count} items across {len(raw)} countries", flush=True)
        else:
            _write_json(RAW / f"{key}.json", raw)
            if do_archive:
                p = _archive_path(key, None, now)
                if not p.exists():
                    _write_json(p, raw)
            print(f"[{key}] {len(raw)} items", flush=True)


if __name__ == "__main__":
    main()
