<div align="center">

<img src="./assets/icon.png" width="96" alt="Trending Pages logo" />

# Trending Pages

**One place. Eleven platforms. What the world is watching, right now.**

[🌐 **Live site**](https://trending.subdownload.com/) · [📦 JSON API](https://trending.subdownload.com/data/latest.json) · [📡 RSS](https://trending.subdownload.com/data/feed.xml) · [🗄 Archive](https://trending.subdownload.com/data/archive/)

![refresh](https://img.shields.io/badge/refresh-every%2030%20min-1ee84d) ![sources](https://img.shields.io/badge/sources-11-1ee84d) ![languages](https://img.shields.io/badge/i18n-7%20languages-1ee84d) ![license](https://img.shields.io/badge/license-MIT-blue)

</div>

---

## What it shows

Real-time trending from 11 of the world's biggest content platforms — refreshed every 30 minutes, history archived twice a day:

**Overseas**

| Platform | What | Region |
|---|---|---|
| 🟥 **YouTube** | `chart=mostPopular` videos | 🇬🇧 🇺🇸 🇯🇵 🇰🇷 🇮🇳 🇭🇰 🇹🇼 |
| 𝕏 **X / Twitter** | trends | global |
| 🟧 **Reddit** | `r/popular` | global |
| 📷 **Instagram** | top hashtags | global |
| 🐙 **GitHub** | trending daily repositories | global |

**China**

| Platform | What | Region |
|---|---|---|
| 🟨 **微博** | 实时热搜 | 🇨🇳 |
| 🔴 **知乎** | 热榜 | 🇨🇳 |
| 🟦 **抖音** | 热搜词 | 🇨🇳 |
| 🟩 **头条** | 头条热榜 | 🇨🇳 |
| 🅱️ **Bilibili** | 全站热门 | 🇨🇳 |
| 🟫 **V2EX** | 热门主题 | 🇨🇳 |

> ℹ️ Twitter via [trends24.in](https://trends24.in/) (latest snapshot). Instagram via [top-hashtags.com](https://top-hashtags.com/instagram/) — Meta doesn't publish a real-time global trending feed, so it's "long-term most-used tags" rather than minute-by-minute movement.

## What you get, for free

- **🌐 Web UI** — Pinterest-style masonry, instant country/source switching, dark mode
- **📦 JSON API** — `data/latest.json` for everything, `data/latest/<source>.json` per platform, `data/latest/youtube/<CC>.json` per country
- **📡 RSS feeds** — `data/feed.xml` combined + per-source `data/feeds/<source>.xml`
- **🗄 Full history** — `data/archive/YY.MM.DD/HH/*.json` snapshots, twice daily, preserved forever
- **🌍 7 languages** — English · 简体中文 · 繁體中文 · 日本語 · 한국어 · Español · हिन्दी
- **⚙️ Self-hostable** — fork it, add your own YouTube key, done

## Use cases

- 📊 **Trend research** — historical archive gives you a year-over-year view of what was hot when
- 🎯 **Content strategy** — see what's working across platforms before you post
- 🤖 **Bot fuel** — JSON API is one HTTP GET away; build dashboards, Slack bots, newsletters
- 📰 **Personal feed** — subscribe to per-platform RSS, skip the doom-scrolling
- 🌏 **Cross-cultural pulse** — compare what's trending in 🇺🇸 vs 🇨🇳 vs 🇯🇵 at a glance

## API at a glance

```bash
# Everything, all sources, latest snapshot
curl https://xatlaz-com.github.io/trending/data/latest.json

# Just YouTube US
curl https://xatlaz-com.github.io/trending/data/latest/youtube/US.json

# Just GitHub trending
curl https://xatlaz-com.github.io/trending/data/latest/github.json

# Just Instagram top hashtags
curl https://xatlaz-com.github.io/trending/data/latest/instagram.json

# Historical: midnight UTC archive for 2026-05-11
curl https://xatlaz-com.github.io/trending/data/archive/26.05.11/00/youtube-GB.json
```

Subscribe in any RSS reader:
```
https://xatlaz-com.github.io/trending/data/feed.xml             # everything
https://xatlaz-com.github.io/trending/data/feeds/youtube-GB.xml
https://xatlaz-com.github.io/trending/data/feeds/weibo.xml
https://xatlaz-com.github.io/trending/data/feeds/instagram.xml
```

---

## Setup (your own fork)

1. Fork → enable GitHub Actions on your fork.
2. Get a free [YouTube Data API v3 key](https://console.cloud.google.com/apis/credentials) (10K units/day free, project uses ~340/day).
3. Settings → Secrets → add `YOUTUBE_DATA_API_KEY`.
4. Settings → Pages → branch `main`, folder `/ (root)`.
5. Actions → run `Scrape Trending` once. Done — it'll refresh every 30 min on its own.

Optional Variables (Settings → Variables):
- `COUNTRIES` — default `GB,US,JP,KR,IN,HK,TW`
- `SOURCES` — default `youtube,twitter,reddit,instagram,github,weibo,zhihu,douyin,toutiao,bilibili,v2ex`
- `ARCHIVE_HOURS` — default `0,12` (UTC hours when snapshots get archived)

## Local dev

```bash
pip install -r requirements.txt
export YOUTUBE_DATA_API_KEY=your_key
python scraper/scrape_all.py
python scraper/generate_outputs.py
python -m http.server 8000   # open http://localhost:8000/
```

## License

[MIT](./LICENSE) © 2026 xAtlaz
