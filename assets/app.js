const DATA_URL = `./data/latest.json?t=${Date.now()}`;

const I18N = {
  "en": { label: "English",
    title: "Trending Pages",
    description_meta: "YouTube / GitHub / V2EX / 微博 / 知乎 / 抖音 / 头条 trending, refreshed every 30 minutes. RSS + JSON API.",
    subtitle: "Refreshed every 30 min ·",
    loading: "loading…", updated_prefix: "updated",
    s_ago: "{0}s ago", m_ago: "{0}m ago",
    nav_json: "latest.json", nav_rss: "RSS", nav_history: "history", nav_source: "source",
    views: "views",
    no_data: "No data yet.",
    failed_load: "Failed to load data: {0}",
    footer_feeds: "Per-source feeds:",
    sources: { youtube: "YouTube", github: "GitHub", v2ex: "V2EX", weibo: "Weibo", zhihu: "Zhihu", douyin: "Douyin", toutiao: "Toutiao", reddit: "Reddit", bilibili: "Bilibili", instagram: "Instagram" },
  },
  "zh-Hans": { label: "简体中文",
    title: "趋势榜单",
    description_meta: "覆盖 YouTube / GitHub / V2EX / 微博 / 知乎 / 抖音 / 头条 的实时榜单，每 30 分钟自动更新，提供 RSS 与 JSON API。",
    subtitle: "每 30 分钟刷新 ·",
    loading: "加载中…", updated_prefix: "更新于",
    s_ago: "{0} 秒前", m_ago: "{0} 分钟前",
    nav_json: "JSON API", nav_rss: "RSS 订阅", nav_history: "历史归档", nav_source: "源码",
    views: "次观看",
    no_data: "暂无数据。",
    failed_load: "数据加载失败：{0}",
    footer_feeds: "分源订阅：",
    sources: { youtube: "YouTube", github: "GitHub 趋势", v2ex: "V2EX", weibo: "微博热搜", zhihu: "知乎热榜", douyin: "抖音热搜", toutiao: "头条热榜", reddit: "Reddit", bilibili: "B 站热门", instagram: "Instagram" },
  },
  "zh-Hant": { label: "繁體中文",
    title: "熱門趨勢",
    description_meta: "涵蓋 YouTube / GitHub / V2EX / 微博 / 知乎 / 抖音 / 頭條 即時榜單，每 30 分鐘自動更新，提供 RSS 與 JSON API。",
    subtitle: "每 30 分鐘更新 ·",
    loading: "載入中…", updated_prefix: "更新於",
    s_ago: "{0} 秒前", m_ago: "{0} 分鐘前",
    nav_json: "JSON API", nav_rss: "RSS 訂閱", nav_history: "歷史封存", nav_source: "原始碼",
    views: "次觀看",
    no_data: "尚無資料。",
    failed_load: "資料載入失敗：{0}",
    footer_feeds: "分源訂閱：",
    sources: { youtube: "YouTube", github: "GitHub 趨勢", v2ex: "V2EX", weibo: "微博熱搜", zhihu: "知乎熱榜", douyin: "抖音熱搜", toutiao: "頭條熱榜", reddit: "Reddit", bilibili: "B 站熱門", instagram: "Instagram" },
  },
  "ja": { label: "日本語",
    title: "トレンドページ",
    description_meta: "YouTube / GitHub / V2EX / 微博 / 知乎 / 抖音 / 头条 のトレンド、30 分ごとに自動更新。RSS と JSON API 提供。",
    subtitle: "30 分ごとに更新 ·",
    loading: "読み込み中…", updated_prefix: "更新",
    s_ago: "{0}秒前", m_ago: "{0}分前",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "履歴", nav_source: "ソース",
    views: "回視聴",
    no_data: "データなし。",
    failed_load: "データ読み込みに失敗：{0}",
    footer_feeds: "ソース別フィード：",
    sources: { youtube: "YouTube", github: "GitHubトレンド", v2ex: "V2EX", weibo: "微博", zhihu: "知乎", douyin: "抖音", toutiao: "今日头条", reddit: "Reddit", bilibili: "Bilibili", instagram: "Instagram" },
  },
  "ko": { label: "한국어",
    title: "트렌딩 페이지",
    description_meta: "YouTube / GitHub / V2EX / 微博 / 知乎 / 抖音 / 头条 트렌드, 30분마다 자동 갱신. RSS 및 JSON API.",
    subtitle: "30분마다 갱신 ·",
    loading: "불러오는 중…", updated_prefix: "업데이트",
    s_ago: "{0}초 전", m_ago: "{0}분 전",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "기록", nav_source: "소스",
    views: "회 시청",
    no_data: "데이터 없음.",
    failed_load: "데이터 로드 실패: {0}",
    footer_feeds: "소스별 피드:",
    sources: { youtube: "YouTube", github: "GitHub 트렌딩", v2ex: "V2EX", weibo: "웨이보", zhihu: "지후", douyin: "더우인", toutiao: "터우탸오", reddit: "Reddit", bilibili: "비리비리", instagram: "인스타그램" },
  },
  "es": { label: "Español",
    title: "Páginas de tendencias",
    description_meta: "Tendencias de YouTube / GitHub / V2EX / Weibo / Zhihu / Douyin / Toutiao, cada 30 min. RSS y API JSON.",
    subtitle: "Actualizado cada 30 min ·",
    loading: "cargando…", updated_prefix: "actualizado",
    s_ago: "hace {0}s", m_ago: "hace {0}m",
    nav_json: "API JSON", nav_rss: "RSS", nav_history: "historial", nav_source: "código",
    views: "visualizaciones",
    no_data: "Aún no hay datos.",
    failed_load: "Error al cargar datos: {0}",
    footer_feeds: "Feeds por fuente:",
    sources: { youtube: "YouTube", github: "GitHub Trending", v2ex: "V2EX", weibo: "Weibo", zhihu: "Zhihu", douyin: "Douyin", toutiao: "Toutiao", reddit: "Reddit", bilibili: "Bilibili", instagram: "Instagram" },
  },
  "hi": { label: "हिन्दी",
    title: "ट्रेंडिंग पेज",
    description_meta: "YouTube / GitHub / V2EX / Weibo / Zhihu / Douyin / Toutiao ट्रेंडिंग, हर 30 मिनट में अपडेट।",
    subtitle: "हर 30 मिनट में रिफ्रेश ·",
    loading: "लोड हो रहा है…", updated_prefix: "अपडेट",
    s_ago: "{0} सेकंड पहले", m_ago: "{0} मिनट पहले",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "इतिहास", nav_source: "स्रोत",
    views: "व्यू",
    no_data: "अभी कोई डेटा नहीं।",
    failed_load: "डेटा लोड विफल: {0}",
    footer_feeds: "स्रोत-वार फ़ीड:",
    sources: { youtube: "YouTube", github: "GitHub Trending", v2ex: "V2EX", weibo: "वेइबो", zhihu: "ज़ीहू", douyin: "डोयिन", toutiao: "तौतियाओ", reddit: "Reddit", bilibili: "बिलिबिली", instagram: "इंस्टाग्राम" },
  },
};
const HTML_LANG = { "en": "en", "zh-Hans": "zh-Hans", "zh-Hant": "zh-Hant", "ja": "ja", "ko": "ko", "es": "es", "hi": "hi" };

function detectLang() {
  const stored = localStorage.getItem("lang");
  if (stored && I18N[stored]) return stored;
  const n = (navigator.language || "en").toLowerCase();
  if (n.startsWith("zh")) return (n.includes("hant") || n.includes("tw") || n.includes("hk") || n.includes("mo")) ? "zh-Hant" : "zh-Hans";
  if (n.startsWith("ja")) return "ja";
  if (n.startsWith("ko")) return "ko";
  if (n.startsWith("es")) return "es";
  if (n.startsWith("hi")) return "hi";
  return "en";
}
let lang = detectLang();
const t = (key, ...args) => {
  const s = (I18N[lang] && I18N[lang][key]) || (I18N.en[key] || key);
  return args.length ? s.replace(/\{(\d+)\}/g, (_, i) => args[+i] ?? "") : s;
};
const sourceLabel = key => (I18N[lang]?.sources?.[key]) || I18N.en.sources?.[key] || key;

const fmtNum = n => n >= 1e6 ? (n / 1e6).toFixed(1) + "M" : n >= 1e3 ? (n / 1e3).toFixed(1) + "K" : String(n ?? 0);
const fmtDuration = iso => {
  if (!iso) return "";
  const m = iso.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!m) return "";
  const h = +m[1] || 0, mn = +m[2] || 0, s = +m[3] || 0;
  return (h ? `${h}:${String(mn).padStart(2, "0")}` : `${mn}`) + `:${String(s).padStart(2, "0")}`;
};
const fmtAgo = iso => {
  const d = new Date(iso), diff = (Date.now() - d) / 1000;
  if (diff < 60) return t("s_ago", Math.floor(diff));
  if (diff < 3600) return t("m_ago", Math.floor(diff / 60));
  return d.toLocaleString();
};
const escapeHtml = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function applyI18n() {
  document.documentElement.lang = HTML_LANG[lang] || "en";
  document.title = t("title");
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-attr]").forEach(el => {
    el.dataset.i18nAttr.split(",").forEach(pair => {
      const [attr, key] = pair.split(":");
      el.setAttribute(attr, t(key));
    });
  });
}

function renderLangSelect() {
  const sel = document.getElementById("lang-select");
  sel.innerHTML = Object.entries(I18N).map(([code, v]) =>
    `<option value="${code}" ${code === lang ? "selected" : ""}>${v.label}</option>`).join("");
  sel.addEventListener("change", () => {
    lang = sel.value;
    localStorage.setItem("lang", lang);
    applyI18n();
    state.rerender?.();
  });
}

function renderSources(sources, currentKey, onSelect) {
  const el = document.getElementById("sources");
  el.innerHTML = sources.map(s =>
    `<button class="src-pill" role="tab" aria-selected="${s.key === currentKey}" data-src="${s.key}">${escapeHtml(sourceLabel(s.key))}</button>`
  ).join("");
  el.querySelectorAll(".src-pill").forEach(b => b.addEventListener("click", () => onSelect(b.dataset.src)));
}

function renderTabs(countries, current, onSelect) {
  const tabs = document.getElementById("tabs");
  if (!countries?.length) { tabs.innerHTML = ""; return; }
  tabs.innerHTML = countries.map(cc =>
    `<button class="tab" role="tab" aria-selected="${cc === current}" data-cc="${cc}">${cc}</button>`).join("");
  tabs.querySelectorAll(".tab").forEach(el => el.addEventListener("click", () => onSelect(el.dataset.cc)));
}

function renderCards(items, sourceKey) {
  const grid = document.getElementById("grid");
  if (!items?.length) { grid.innerHTML = `<div class="empty">${escapeHtml(t("no_data"))}</div>`; return; }
  grid.innerHTML = items.map(it => {
    const img = it.image;
    const isYT = sourceKey === "youtube";
    const dur = isYT && it.extra?.duration ? fmtDuration(it.extra.duration) : null;
    const metricStr = isYT && typeof it.metric_value === "number"
      ? `${fmtNum(it.metric_value)} ${escapeHtml(t("views"))}`
      : escapeHtml(it.metric || "");
    if (img) {
      return `<article class="card">
        <a class="thumb" href="${escapeHtml(it.url)}" target="_blank" rel="noopener">
          <img loading="lazy" src="${escapeHtml(img)}" alt="">
          <span class="rank">#${it.rank}</span>
        </a>
        <div class="body">
          <a class="title" href="${escapeHtml(it.url)}" target="_blank" rel="noopener">${escapeHtml(it.title || "")}</a>
          <div class="meta">
            ${it.channel ? `<span>${escapeHtml(it.channel)}</span>` : ""}
            ${metricStr ? `<span>${metricStr}</span>` : ""}
            ${dur ? `<span>${dur}</span>` : ""}
          </div>
        </div>
      </article>`;
    }
    const language = it.extra?.language;
    const stars_today = it.extra?.stars_today;
    return `<article class="card no-thumb">
      <div class="body">
        <a class="title" href="${escapeHtml(it.url)}" target="_blank" rel="noopener">
          <span class="rank-inline">#${it.rank}</span>${escapeHtml(it.title || "")}
        </a>
        ${it.description ? `<div class="desc">${escapeHtml(it.description)}</div>` : ""}
        <div class="meta">
          ${language ? `<span class="lang">${escapeHtml(language)}</span>` : ""}
          ${metricStr ? `<span>${metricStr}</span>` : ""}
          ${stars_today ? `<span>${escapeHtml(stars_today)}</span>` : ""}
          ${it.extra?.node ? `<span>${escapeHtml(it.extra.node)}</span>` : ""}
          ${it.extra?.author ? `<span>@${escapeHtml(it.extra.author)}</span>` : ""}
        </div>
      </div>
    </article>`;
  }).join("");
}

function renderFeeds(sources) {
  const el = document.getElementById("per-source-feeds");
  el.innerHTML = sources.map(s => {
    if (s.kind === "multi-country") {
      return `${escapeHtml(sourceLabel(s.key))}: ` + s.countries.map(cc =>
        `<a href="./data/feeds/${s.key}-${cc}.xml">${cc}</a>`).join(" ");
    }
    return `<a href="./data/feeds/${s.key}.xml">${escapeHtml(sourceLabel(s.key))}</a>`;
  }).join(" · ");
}

function renderUpdated(iso) {
  document.getElementById("updated").textContent = `${t("updated_prefix")} ${fmtAgo(iso)}`;
}

const state = {};

let masonryRO = null;
let masonryTimer = null;
const MASONRY_GAP = 14;
const MASONRY_MIN_WIDTH = 280;

function layoutMasonry() {
  const grid = document.getElementById("grid");
  if (!grid) return;
  const cards = [...grid.querySelectorAll(".card")];
  if (!cards.length) { grid.style.height = ""; return; }
  const w = grid.clientWidth;
  if (w <= 0) return;
  const numCols = Math.max(1, Math.floor((w + MASONRY_GAP) / (MASONRY_MIN_WIDTH + MASONRY_GAP)));
  const colWidth = (w - MASONRY_GAP * (numCols - 1)) / numCols;
  const colHeights = new Array(numCols).fill(0);
  cards.forEach(card => {
    card.style.width = colWidth + "px";
    let minIdx = 0;
    for (let i = 1; i < numCols; i++) {
      if (colHeights[i] < colHeights[minIdx]) minIdx = i;
    }
    const x = minIdx * (colWidth + MASONRY_GAP);
    const y = colHeights[minIdx];
    card.style.left = x + "px";
    card.style.top = y + "px";
    colHeights[minIdx] += card.offsetHeight + MASONRY_GAP;
  });
  grid.style.height = (Math.max(...colHeights) - MASONRY_GAP) + "px";
}

function relayoutSoon() {
  if (masonryTimer) return;
  masonryTimer = requestAnimationFrame(() => {
    masonryTimer = null;
    layoutMasonry();
  });
}

function setupMasonry() {
  const grid = document.getElementById("grid");
  if (!grid) return;
  if (masonryRO) masonryRO.disconnect();
  masonryRO = new ResizeObserver(relayoutSoon);
  masonryRO.observe(grid);
  grid.querySelectorAll(".card").forEach(c => masonryRO.observe(c));
  grid.querySelectorAll("img").forEach(img => {
    if (!img.complete) {
      img.addEventListener("load", relayoutSoon, { once: true });
      img.addEventListener("error", relayoutSoon, { once: true });
    }
  });
  layoutMasonry();
}

window.addEventListener("resize", relayoutSoon);

(async function init() {
  applyI18n();
  renderLangSelect();
  let payload;
  try {
    payload = await fetch(DATA_URL).then(r => r.json());
  } catch (e) {
    document.getElementById("grid").innerHTML = `<div class="empty">${escapeHtml(t("failed_load", e.message))}</div>`;
    return;
  }
  const sources = payload.sources || [];
  if (!sources.length) {
    document.getElementById("grid").innerHTML = `<div class="empty">${escapeHtml(t("no_data"))}</div>`;
    return;
  }
  renderUpdated(payload.updated_at);

  const hash = decodeURIComponent(location.hash.replace(/^#/, ""));
  let [initSrc, initCC] = hash.split("/");
  if (!sources.find(s => s.key === initSrc)) initSrc = sources[0].key;
  let currentSrc = initSrc;
  let currentCC = initCC;

  function syncHash() {
    const meta = sources.find(s => s.key === currentSrc);
    history.replaceState(null, "", "#" + currentSrc + (meta.kind === "multi-country" ? `/${currentCC}` : ""));
  }

  function selectSrc(key) {
    currentSrc = key;
    const meta = sources.find(s => s.key === key);
    if (meta.kind === "multi-country") {
      if (!meta.countries.includes(currentCC)) currentCC = meta.countries[0];
    } else {
      currentCC = undefined;
    }
    syncHash();
    state.rerender();
  }

  function selectCC(cc) {
    currentCC = cc;
    syncHash();
    state.rerender();
  }

  state.rerender = () => {
    renderSources(sources, currentSrc, selectSrc);
    const meta = sources.find(s => s.key === currentSrc);
    if (meta.kind === "multi-country") {
      renderTabs(meta.countries, currentCC, selectCC);
      renderCards(payload.data[currentSrc]?.[currentCC] || [], currentSrc);
    } else {
      renderTabs([], null, () => {});
      renderCards(payload.data[currentSrc] || [], currentSrc);
    }
    renderFeeds(sources);
    renderUpdated(payload.updated_at);
    setupMasonry();
  };

  if (!currentCC) {
    const meta = sources.find(s => s.key === currentSrc);
    if (meta.kind === "multi-country") currentCC = meta.countries[0];
  }
  syncHash();
  state.rerender();
})();
