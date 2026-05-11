# Trending Pages

YouTube trending videos across regions — auto-refreshed every 30 minutes, with full historical archive, JSON API, and RSS feeds. Hosted as a static site on GitHub Pages.

## What you get

- **Web UI** — `https://<user>.github.io/<repo>/` — country tabs, thumbnails, ranks, views
- **JSON API** — always the latest snapshot
  - `data/latest.json` — all countries combined
  - `data/latest/<CC>.json` — single country (e.g. `data/latest/US.json`)
- **RSS feeds**
  - `data/feed.xml` — all countries combined
  - `data/feeds/<CC>.xml` — single country
- **History archive** — `data/archive/YY.MM.DD/<HH>/<CC>.json` (raw API responses, **2 snapshots per day** by default at UTC 00:00 and 12:00)

## Setup (one time)

1. Push this repo to GitHub.
2. **Secrets** — Settings → Secrets and variables → Actions → New repository secret:
   - `YOUTUBE_DATA_API_KEY` — your YouTube Data API v3 key ([Google Cloud Console](https://console.cloud.google.com/apis/credentials), free 10 000 units/day quota; this project uses ~340/day at 30-min intervals × 7 countries).
3. **(Optional) Variables** — Settings → Secrets and variables → Actions → Variables:
   - `COUNTRIES` — comma-separated ISO codes. Default `US,JP,KR,GB,IN,HK,TW`.
   - `ARCHIVE_HOURS` — comma-separated UTC hours at which to snapshot to `data/archive/`. Default `0,12` (twice a day). The scraper still runs every 30 min for fresh `latest.json` / RSS, but only writes to archive at these slots.
4. **GitHub Pages** — Settings → Pages → Source: `Deploy from a branch` → branch `main`, folder `/ (root)`.
5. **Run it once** — Actions tab → `Scrape YouTube Trending` → `Run workflow`. After it completes, your site is live and will refresh every 30 min.

## Local dev

```bash
pip install -r requirements.txt
export YOUTUBE_DATA_API_KEY=your_key_here
export COUNTRIES=US,JP
python scraper/youtube_scraper.py
python scraper/generate_outputs.py
python -m http.server 8000   # open http://localhost:8000/
```

## Notes

- GitHub Actions cron is best-effort; expect ±5–15 min drift during peak hours. The archive slot logic is idempotent — first run within an archive hour wins, retries are no-ops.
- `data/raw/<CC>.json` is overwritten every run (not committed history). Only `data/archive/` keeps long-term snapshots.
- At 2 snapshots/day × 7 countries × ~250 KB/country, archive grows ~3.5 MB/day, ~1.3 GB/year. Manageable in a regular repo for years.
- `latest.json` and per-country files are **simplified** (rank, title, channel, views, thumbnail, duration, url). Raw API responses live in `data/raw/` (current) and `data/archive/` (historical).

## License

[MIT](./LICENSE) © 2026 xAtlaz
