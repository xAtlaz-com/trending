"""
Render static HTML pages from data/latest/* snapshots.

Outputs:
  index.html                              — hub page listing all sources with previews
  <key>/index.html                        — single-source page (e.g. /twitter/, /github/)
  <key>/<CC>/index.html                   — multi-country sub-page (e.g. /youtube/GB/)
  <key>/index.html (multi-country)        — meta-refresh redirect to default country

Each page ships with:
  - unique <title>, meta description, canonical
  - OpenGraph + Twitter Card tags
  - ItemList JSON-LD with every ranked entry
  - <link rel="alternate"> for the matching JSON and RSS endpoints
  - cross-links to siblings so crawlers can hop between sources

Run after generate_outputs.py.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LATEST = DATA / "latest"

BASE_URL = "https://trending.subdownload.com"
SITE_TITLE = "Trending Pages"

# Display order for source pills. Matches the env-default in generate_outputs.py.
SOURCE_ORDER = [
    "youtube", "twitter", "reddit", "instagram", "github",
    "weibo", "zhihu", "douyin", "toutiao", "bilibili", "v2ex",
]

# Country display order for YouTube; default = first found.
COUNTRY_ORDER = ["GB", "US", "JP", "KR", "IN", "HK", "TW"]

# Per-source metadata used for SEO chrome.
SOURCE_META: dict[str, dict] = {
    "youtube": {
        "label": "YouTube",
        "kind": "multi-country",
        "title": "YouTube Trending — {cc_name}",
        "description": "Top YouTube videos trending in {cc_name} right now. Refreshed every 30 minutes. Free JSON + RSS.",
        "keywords": "youtube trending, youtube popular, viral videos, {cc_name} trending",
    },
    "twitter": {
        "label": "X / Twitter Trends",
        "kind": "single",
        "title": "X (Twitter) Trends — Worldwide",
        "description": "Real-time X / Twitter trending hashtags and topics, refreshed every 30 minutes. Free JSON + RSS.",
        "keywords": "x trends, twitter trends, trending hashtags, viral topics",
    },
    "reddit": {
        "label": "Reddit r/popular",
        "kind": "single",
        "title": "Reddit Popular — Top trending posts",
        "description": "What's hot on Reddit right now — top posts from r/popular, refreshed every 30 minutes. Free JSON + RSS.",
        "keywords": "reddit popular, reddit trending, top reddit posts, viral reddit",
    },
    "instagram": {
        "label": "Instagram Hashtags",
        "kind": "single",
        "title": "Top Instagram Hashtags — Real-time",
        "description": "Live ranking of the most popular Instagram hashtags worldwide. Refreshed every 30 minutes. Free JSON + RSS.",
        "keywords": "instagram hashtags, trending hashtags, popular instagram",
    },
    "github": {
        "label": "GitHub Trending",
        "kind": "single",
        "title": "GitHub Trending Repositories — Daily",
        "description": "Fastest-rising GitHub repositories. Daily trending across all languages, refreshed every 30 minutes. Free JSON + RSS.",
        "keywords": "github trending, trending repositories, github popular, open source trending",
    },
    "weibo": {
        "label": "微博热搜",
        "kind": "single",
        "title": "微博热搜 — Real-time Weibo Hot Search",
        "description": "微博实时热搜榜单，每 30 分钟自动更新。Real-time Weibo hot-search ranking, refreshed every 30 minutes. Free JSON + RSS.",
        "keywords": "微博热搜, weibo hot search, 实时热搜, weibo trending",
    },
    "zhihu": {
        "label": "知乎热榜",
        "kind": "single",
        "title": "知乎热榜 — Real-time Zhihu Hot Topics",
        "description": "知乎实时热榜，每 30 分钟自动更新。Real-time Zhihu hot-topic ranking. Free JSON + RSS.",
        "keywords": "知乎热榜, zhihu hot, zhihu trending, 知乎实时",
    },
    "douyin": {
        "label": "抖音热搜",
        "kind": "single",
        "title": "抖音热搜 — Real-time Douyin Hot Search",
        "description": "抖音实时热搜榜单，每 30 分钟刷新。Real-time Douyin (China TikTok) hot-search ranking. Free JSON + RSS.",
        "keywords": "抖音热搜, douyin hot search, douyin trending, 抖音实时",
    },
    "toutiao": {
        "label": "头条热榜",
        "kind": "single",
        "title": "今日头条热榜 — Real-time Toutiao Hot News",
        "description": "今日头条实时热榜，每 30 分钟更新。Real-time Toutiao hot-news ranking. Free JSON + RSS.",
        "keywords": "头条热榜, toutiao hot, toutiao trending, 今日头条",
    },
    "bilibili": {
        "label": "Bilibili 全站热门",
        "kind": "single",
        "title": "Bilibili 全站热门 — Real-time",
        "description": "Bilibili 全站热门视频实时榜单，每 30 分钟刷新。Real-time Bilibili popular video ranking. Free JSON + RSS.",
        "keywords": "bilibili 热门, B 站热门, bilibili trending, bilibili popular",
    },
    "v2ex": {
        "label": "V2EX",
        "kind": "single",
        "title": "V2EX Hot Topics — Real-time",
        "description": "V2EX 实时热门主题，每 30 分钟刷新。Real-time V2EX hot-topic ranking. Free JSON + RSS.",
        "keywords": "v2ex 热门, v2ex trending, v2ex hot topics",
    },
}

COUNTRY_NAMES = {
    "GB": "United Kingdom", "US": "United States", "JP": "Japan",
    "KR": "South Korea", "IN": "India", "HK": "Hong Kong", "TW": "Taiwan",
}


def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def fmt_num(n) -> str:
    try:
        n = float(n)
    except (TypeError, ValueError):
        return ""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


_DUR_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def fmt_duration(iso: str | None) -> str:
    if not iso:
        return ""
    m = _DUR_RE.match(iso)
    if not m:
        return ""
    h = int(m.group(1) or 0)
    mn = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    if h:
        return f"{h}:{mn:02d}:{s:02d}"
    return f"{mn}:{s:02d}"


def render_card(it: dict, source_key: str) -> str:
    img = it.get("image")
    is_yt = source_key == "youtube"
    extra = it.get("extra") or {}
    dur = fmt_duration(extra.get("duration")) if is_yt else ""
    if is_yt and isinstance(it.get("metric_value"), (int, float)):
        metric_str = f"{fmt_num(it['metric_value'])} views"
    else:
        metric_str = it.get("metric") or ""

    rank = it.get("rank") or ""
    title = it.get("title") or ""
    url = it.get("url") or "#"

    if img:
        meta_parts = []
        if it.get("channel"):
            meta_parts.append(f"<span>{esc(it['channel'])}</span>")
        if metric_str:
            meta_parts.append(f"<span>{esc(metric_str)}</span>")
        if dur:
            meta_parts.append(f"<span>{esc(dur)}</span>")
        return (
            '<article class="card">'
            f'<a class="thumb" href="{esc(url)}" target="_blank" rel="noopener">'
            f'<img loading="lazy" referrerpolicy="no-referrer" src="{esc(img)}" alt="">'
            f'<span class="rank">#{esc(rank)}</span>'
            '</a>'
            '<div class="body">'
            f'<a class="title" href="{esc(url)}" target="_blank" rel="noopener">{esc(title)}</a>'
            f'<div class="meta">{"".join(meta_parts)}</div>'
            '</div>'
            '</article>'
        )

    language = extra.get("language")
    stars_today = extra.get("stars_today")
    node = extra.get("node")
    author = extra.get("author")
    desc = it.get("description")

    meta_parts = []
    if language:
        meta_parts.append(f'<span class="lang">{esc(language)}</span>')
    if metric_str:
        meta_parts.append(f"<span>{esc(metric_str)}</span>")
    if stars_today:
        meta_parts.append(f"<span>{esc(stars_today)}</span>")
    if node:
        meta_parts.append(f"<span>{esc(node)}</span>")
    if author:
        meta_parts.append(f"<span>@{esc(author)}</span>")
    desc_html = f'<div class="desc">{esc(desc)}</div>' if desc else ""
    return (
        '<article class="card no-thumb">'
        '<div class="body">'
        f'<a class="title" href="{esc(url)}" target="_blank" rel="noopener">'
        f'<span class="rank-inline">#{esc(rank)}</span>{esc(title)}'
        '</a>'
        f'{desc_html}'
        f'<div class="meta">{"".join(meta_parts)}</div>'
        '</div>'
        '</article>'
    )


def load_payload(key: str, country: str | None = None) -> dict | None:
    path = LATEST / key / f"{country}.json" if country else LATEST / f"{key}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def available_sources() -> list[tuple[str, str | None]]:
    """Return [(source_key, country_or_None), ...] for sources that have data."""
    out: list[tuple[str, str | None]] = []
    for key in SOURCE_ORDER:
        meta = SOURCE_META.get(key)
        if not meta:
            continue
        if meta["kind"] == "multi-country":
            d = LATEST / key
            if not d.is_dir():
                continue
            found = sorted(p.stem for p in d.glob("*.json"))
            known = [c for c in COUNTRY_ORDER if c in found]
            extra = sorted(c for c in found if c not in COUNTRY_ORDER)
            for cc in known + extra:
                out.append((key, cc))
        else:
            if (LATEST / f"{key}.json").exists():
                out.append((key, None))
    return out


def first_country(key: str) -> str | None:
    d = LATEST / key
    if not d.is_dir():
        return None
    found = sorted(p.stem for p in d.glob("*.json"))
    for cc in COUNTRY_ORDER:
        if cc in found:
            return cc
    return found[0] if found else None


def page_url(key: str, country: str | None = None) -> str:
    if country:
        return f"{BASE_URL}/{key}/{country}/"
    return f"{BASE_URL}/{key}/"


def page_rel_path(key: str, country: str | None = None) -> str:
    if country:
        return f"./{key}/{country}/"
    return f"./{key}/"


def source_label(key: str) -> str:
    return SOURCE_META.get(key, {}).get("label", key)


def page_title(key: str, country: str | None) -> str:
    meta = SOURCE_META[key]
    tmpl = meta["title"]
    if "{cc_name}" in tmpl:
        return tmpl.format(cc_name=COUNTRY_NAMES.get(country or "", country or ""))
    return tmpl


def page_description(key: str, country: str | None) -> str:
    meta = SOURCE_META[key]
    tmpl = meta["description"]
    if "{cc_name}" in tmpl:
        return tmpl.format(cc_name=COUNTRY_NAMES.get(country or "", country or ""))
    return tmpl


def render_sources_nav(active_key: str, prefix: str = "./") -> str:
    parts = ['<nav class="sources" aria-label="Source">']
    for key in SOURCE_ORDER:
        if key not in SOURCE_META:
            continue
        meta = SOURCE_META[key]
        cc = first_country(key) if meta["kind"] == "multi-country" else None
        if meta["kind"] == "multi-country" and not cc:
            continue
        href = f"{prefix}{key}/{cc}/" if cc else f"{prefix}{key}/"
        active = ' aria-current="page"' if key == active_key else ""
        parts.append(
            f'<a class="src-pill" href="{esc(href)}"{active}>{esc(meta["label"])}</a>'
        )
    parts.append("</nav>")
    return "".join(parts)


def render_country_tabs(key: str, active_cc: str, prefix: str = "../../") -> str:
    d = LATEST / key
    if not d.is_dir():
        return ""
    found = sorted(p.stem for p in d.glob("*.json"))
    known = [c for c in COUNTRY_ORDER if c in found]
    extra = sorted(c for c in found if c not in COUNTRY_ORDER)
    countries = known + extra
    if not countries:
        return ""
    parts = [f'<nav class="tabs" aria-label="{esc(key)} country">']
    for cc in countries:
        href = f"{prefix}{key}/{cc}/"
        active = ' aria-current="page"' if cc == active_cc else ""
        label = f"{cc}"
        parts.append(f'<a class="tab" href="{esc(href)}"{active} title="{esc(COUNTRY_NAMES.get(cc, cc))}">{esc(label)}</a>')
    parts.append("</nav>")
    return "".join(parts)


def render_feeds_footer(prefix: str = "./") -> str:
    bits: list[str] = []
    for key in SOURCE_ORDER:
        meta = SOURCE_META.get(key)
        if not meta:
            continue
        if meta["kind"] == "multi-country":
            d = LATEST / key
            if not d.is_dir():
                continue
            found = sorted(p.stem for p in d.glob("*.json"))
            known = [c for c in COUNTRY_ORDER if c in found]
            extra = sorted(c for c in found if c not in COUNTRY_ORDER)
            country_links = " ".join(
                f'<a href="{prefix}data/feeds/{key}-{cc}.xml">{esc(cc)}</a>'
                for cc in known + extra
            )
            if country_links:
                bits.append(f"{esc(meta['label'])}: {country_links}")
        else:
            if (LATEST / f"{key}.json").exists():
                bits.append(f'<a href="{prefix}data/feeds/{key}.xml">{esc(meta["label"])}</a>')
    return " · ".join(bits)


def fmt_updated_ago(iso: str) -> str:
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return iso
    diff = (datetime.now(timezone.utc) - d).total_seconds()
    if diff < 60:
        return f"updated {int(diff)}s ago"
    if diff < 3600:
        return f"updated {int(diff / 60)}m ago"
    return f"updated {d.strftime('%Y-%m-%d %H:%M UTC')}"


def itemlist_jsonld(items: list[dict], page_url_str: str, name: str) -> str:
    elements = []
    for it in items[:100]:
        if not it.get("url"):
            continue
        el = {
            "@type": "ListItem",
            "position": it.get("rank") or len(elements) + 1,
            "url": it["url"],
            "name": it.get("title") or it["url"],
        }
        if it.get("image"):
            el["image"] = it["image"]
        elements.append(el)
    payload = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "url": page_url_str,
        "numberOfItems": len(elements),
        "itemListElement": elements,
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def og_locales() -> str:
    return (
        '<meta property="og:locale" content="en_US" />'
        '<meta property="og:locale:alternate" content="zh_CN" />'
        '<meta property="og:locale:alternate" content="zh_TW" />'
        '<meta property="og:locale:alternate" content="ja_JP" />'
        '<meta property="og:locale:alternate" content="ko_KR" />'
        '<meta property="og:locale:alternate" content="es_ES" />'
        '<meta property="og:locale:alternate" content="hi_IN" />'
    )


def relpath_to_root(depth: int) -> str:
    return "../" * depth if depth else "./"


def render_source_page(key: str, country: str | None, payload: dict) -> str:
    items = payload.get("items") or []
    updated_at = payload.get("updated_at", "")
    meta = SOURCE_META[key]
    depth = 2 if country else 1
    root = relpath_to_root(depth)

    title = page_title(key, country)
    desc = page_description(key, country)
    canonical = page_url(key, country)
    keywords = meta["keywords"].format(cc_name=COUNTRY_NAMES.get(country or "", country or "")) if country else meta["keywords"]
    og_image = f"{BASE_URL}/assets/icon.png"

    if country:
        json_rel = f"{root}data/latest/{key}/{country}.json"
        rss_rel = f"{root}data/feeds/{key}-{country}.xml"
    else:
        json_rel = f"{root}data/latest/{key}.json"
        rss_rel = f"{root}data/feeds/{key}.xml"

    cards_html = "".join(render_card(it, key) for it in items)
    if not cards_html:
        cards_html = '<div class="empty">No data yet.</div>'

    country_tabs = render_country_tabs(key, country or "", prefix=root) if meta["kind"] == "multi-country" else ""
    sources_nav = render_sources_nav(key, prefix=root)
    feeds_footer = render_feeds_footer(prefix=root)
    jsonld = itemlist_jsonld(items, canonical, title)
    updated_label = fmt_updated_ago(updated_at)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title data-i18n-skip>{esc(title)} · {esc(SITE_TITLE)}</title>
<meta name="description" content="{esc(desc)}" />
<meta name="keywords" content="{esc(keywords)}" />
<meta name="robots" content="index,follow" />
<meta name="googlebot" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
<meta name="theme-color" content="#0b0d10" />
<link rel="canonical" href="{esc(canonical)}" />
<link rel="icon" type="image/png" href="{esc(root)}assets/icon.png" />
<link rel="apple-touch-icon" href="{esc(root)}assets/icon.png" />
<link rel="alternate" type="application/rss+xml" title="{esc(title)} — RSS" href="{esc(rss_rel)}" />
<link rel="alternate" type="application/json" title="{esc(title)} — JSON" href="{esc(json_rel)}" />
<link rel="stylesheet" href="{esc(root)}assets/style.css" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="{esc(SITE_TITLE)}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:url" content="{esc(canonical)}" />
<meta property="og:image" content="{esc(og_image)}" />
{og_locales()}
<meta name="twitter:card" content="summary" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
<meta name="twitter:image" content="{esc(og_image)}" />
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<header>
  <div class="brand">
    <a href="{esc(root)}" style="display:flex;align-items:center;gap:12px;text-decoration:none;color:inherit;flex:1;">
      <img src="{esc(root)}assets/icon.png" alt="{esc(SITE_TITLE)} logo" class="logo" />
      <h1>{esc(SITE_TITLE)}</h1>
    </a>
    <select id="lang-select" class="lang-select" aria-label="Language"></select>
  </div>
  <p class="sub"><span data-i18n="subtitle">Refreshed every 30 min ·</span> <span id="updated" data-updated-at="{esc(updated_at)}">{esc(updated_label)}</span></p>
  <nav class="links" aria-label="Resources">
    <a href="{esc(json_rel)}" data-i18n="nav_json">JSON</a>
    <a href="{esc(rss_rel)}" data-i18n="nav_rss">RSS</a>
    <a href="{esc(root)}data/archive/" data-i18n="nav_history">history</a>
    <a href="https://github.com/xAtlaz-com/trending" target="_blank" rel="noopener" data-i18n="nav_source">source</a>
  </nav>
</header>
{sources_nav}
{country_tabs}
<main class="grid-wrap"><div class="grid">{cards_html}</div></main>
<footer>
  <p><span data-i18n="footer_feeds">Per-source feeds:</span> {feeds_footer}</p>
  <p style="margin-top:8px">
    Other sources: {" · ".join(
        f'<a href="{esc(root)}{k}/' + (f"{first_country(k)}/" if SOURCE_META[k]["kind"] == "multi-country" else "") + f'">{esc(SOURCE_META[k]["label"])}</a>'
        for k in SOURCE_ORDER
        if k != key and k in SOURCE_META and (
            (SOURCE_META[k]["kind"] == "single" and (LATEST / f"{k}.json").exists())
            or (SOURCE_META[k]["kind"] == "multi-country" and first_country(k))
        )
    )}
  </p>
</footer>
<script src="{esc(root)}assets/app.js"></script>
</body>
</html>
"""


def render_hub_page() -> str:
    sections: list[str] = []
    for key in SOURCE_ORDER:
        meta = SOURCE_META.get(key)
        if not meta:
            continue
        if meta["kind"] == "multi-country":
            cc = first_country(key)
            if not cc:
                continue
            payload = load_payload(key, cc)
            href = f"./{key}/{cc}/"
            sublabel = f" — {COUNTRY_NAMES.get(cc, cc)}"
        else:
            payload = load_payload(key)
            href = f"./{key}/"
            sublabel = ""
        if not payload:
            continue
        items = payload.get("items") or []
        preview_count = 6
        cards_html = "".join(render_card(it, key) for it in items[:preview_count])
        if not cards_html:
            continue
        sections.append(
            f'<section class="hub-section">'
            f'<div class="section-head">'
            f'<h2>{esc(meta["label"])}<span class="sub-label">{esc(sublabel)}</span></h2>'
            f'<a class="more" href="{esc(href)}">View all →</a>'
            f'</div>'
            f'<div class="hub-grid-wrap"><div class="grid">{cards_html}</div></div>'
            f'</section>'
        )

    # Updated label from any available payload
    updated_iso = ""
    combined = DATA / "latest.json"
    if combined.exists():
        try:
            updated_iso = json.loads(combined.read_text(encoding="utf-8")).get("updated_at", "")
        except Exception:
            pass
    updated_label = fmt_updated_ago(updated_iso) if updated_iso else ""

    feeds_footer = render_feeds_footer(prefix="./")
    sources_nav = render_sources_nav("", prefix="./")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Trending Pages — Real-time trends from YouTube, X, Reddit, GitHub, Weibo &amp; more</title>
<meta name="description" content="Track what's trending across YouTube, X/Twitter, Reddit, Instagram, GitHub, Weibo, Zhihu, Douyin, Toutiao, Bilibili and V2EX. Refreshed every 30 minutes. Free JSON API and RSS feeds." />
<meta name="keywords" content="trending, trends, youtube trending, twitter trends, x trends, reddit popular, github trending, weibo hot search, 微博热搜, douyin, 抖音热搜, zhihu, 知乎热榜, bilibili, 头条, instagram hashtags, v2ex, real-time trends, json api, rss feed" />
<meta name="robots" content="index,follow" />
<meta name="googlebot" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />
<meta name="theme-color" content="#0b0d10" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="Trending" />
<link rel="canonical" href="{BASE_URL}/" />
<link rel="icon" type="image/png" href="./assets/icon.png" />
<link rel="apple-touch-icon" href="./assets/icon.png" />
<link rel="alternate" type="application/rss+xml" title="Trending — all sources" href="./data/feed.xml" />
<link rel="alternate" type="application/json" title="Trending — JSON API" href="./data/latest.json" />
<link rel="stylesheet" href="./assets/style.css" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Trending Pages" />
<meta property="og:title" content="Trending Pages — Real-time cross-platform trends" />
<meta property="og:description" content="What the world is watching, right now. YouTube, X, Reddit, Instagram, GitHub, Weibo, Zhihu, Douyin, Toutiao, Bilibili &amp; V2EX — refreshed every 30 min." />
<meta property="og:url" content="{BASE_URL}/" />
<meta property="og:image" content="{BASE_URL}/assets/icon.png" />
{og_locales()}
<meta name="twitter:card" content="summary" />
<meta name="twitter:title" content="Trending Pages — Real-time cross-platform trends" />
<meta name="twitter:description" content="11 platforms, refreshed every 30 min." />
<meta name="twitter:image" content="{BASE_URL}/assets/icon.png" />
<script type="application/ld+json">{json.dumps({
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "WebSite",
            "@id": f"{BASE_URL}/#website",
            "url": f"{BASE_URL}/",
            "name": "Trending Pages",
            "description": "Real-time trending content from 11 platforms — refreshed every 30 minutes.",
            "inLanguage": ["en", "zh-Hans", "zh-Hant", "ja", "ko", "es", "hi"],
            "publisher": {"@id": f"{BASE_URL}/#org"},
        },
        {
            "@type": "Organization",
            "@id": f"{BASE_URL}/#org",
            "name": "Trending Pages",
            "url": f"{BASE_URL}/",
            "logo": {"@type": "ImageObject", "url": f"{BASE_URL}/assets/icon.png", "width": 256, "height": 256},
        },
    ],
}, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>
<header>
  <div class="brand">
    <img src="./assets/icon.png" alt="Trending Pages logo" class="logo" />
    <h1>Trending Pages</h1>
    <select id="lang-select" class="lang-select" aria-label="Language"></select>
  </div>
  <p class="sub"><span data-i18n="subtitle">Refreshed every 30 min ·</span> <span id="updated" data-updated-at="{esc(updated_iso)}">{esc(updated_label)}</span></p>
  <nav class="links" aria-label="Resources">
    <a href="./data/latest.json" data-i18n="nav_json">latest.json</a>
    <a href="./data/feed.xml" data-i18n="nav_rss">RSS</a>
    <a href="./data/archive/" data-i18n="nav_history">history</a>
    <a href="https://github.com/xAtlaz-com/trending" target="_blank" rel="noopener" data-i18n="nav_source">source</a>
  </nav>
</header>
{sources_nav}
{"".join(sections)}
<footer>
  <p><span data-i18n="footer_feeds">Per-source feeds:</span> {feeds_footer}</p>
</footer>
<script src="./assets/app.js"></script>
</body>
</html>
"""


def render_redirect_page(target_rel: str, target_label: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Redirecting to {esc(target_label)} · Trending Pages</title>
<meta http-equiv="refresh" content="0; url={esc(target_rel)}" />
<link rel="canonical" href="{esc(target_rel)}" />
<meta name="robots" content="noindex,follow" />
</head>
<body>
<p>Redirecting to <a href="{esc(target_rel)}">{esc(target_label)}</a>…</p>
<script>location.replace({json.dumps(target_rel)});</script>
</body>
</html>
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    written = 0
    pairs = available_sources()
    if not pairs:
        print("no source data found under data/latest/")
        return

    # Per-source / per-country pages
    for key, country in pairs:
        payload = load_payload(key, country)
        if not payload:
            continue
        html_doc = render_source_page(key, country, payload)
        if country:
            write(ROOT / key / country / "index.html", html_doc)
        else:
            write(ROOT / key / "index.html", html_doc)
        written += 1

    # Multi-country sources also get a /{key}/ redirect to default country
    for key in {k for k, _ in pairs if SOURCE_META.get(k, {}).get("kind") == "multi-country"}:
        cc = first_country(key)
        if not cc:
            continue
        target = page_url(key, cc) + ""  # canonical absolute
        write(
            ROOT / key / "index.html",
            render_redirect_page(target_rel=f"./{cc}/", target_label=f"{source_label(key)} — {COUNTRY_NAMES.get(cc, cc)}"),
        )
        written += 1

    # Hub page
    write(ROOT / "index.html", render_hub_page())
    written += 1

    print(f"pages: wrote {written} HTML files")


if __name__ == "__main__":
    main()
