const DATA_URL = `./data/latest.json?t=${Date.now()}`;

const I18N = {
  "en": { label: "English",
    title: "Trending Pages",
    description_meta: "YouTube trending videos across regions, refreshed every 30 minutes. RSS + JSON API included.",
    subtitle: "YouTube · refreshed every 30 min ·",
    loading: "loading…", updated_prefix: "updated",
    s_ago: "{0}s ago", m_ago: "{0}m ago",
    nav_json: "latest.json", nav_rss: "RSS", nav_history: "history", nav_source: "source",
    views: "views",
    no_data: "No data yet. The scraper hasn't run.",
    failed_load: "Failed to load data: {0}",
    footer_via: "Data via YouTube Data API v3.",
    footer_feeds: "Per-country feeds:",
  },
  "zh-Hans": { label: "简体中文",
    title: "趋势榜单",
    description_meta: "覆盖多地区的 YouTube 热门视频，每 30 分钟自动更新。同时提供 RSS 与 JSON API。",
    subtitle: "YouTube · 每 30 分钟刷新 ·",
    loading: "加载中…", updated_prefix: "更新于",
    s_ago: "{0} 秒前", m_ago: "{0} 分钟前",
    nav_json: "JSON API", nav_rss: "RSS 订阅", nav_history: "历史归档", nav_source: "源码",
    views: "次观看",
    no_data: "暂无数据，抓取任务还未执行。",
    failed_load: "数据加载失败：{0}",
    footer_via: "数据来自 YouTube Data API v3。",
    footer_feeds: "各国订阅源：",
  },
  "zh-Hant": { label: "繁體中文",
    title: "熱門趨勢",
    description_meta: "涵蓋多地區的 YouTube 熱門影片，每 30 分鐘自動更新，同時提供 RSS 與 JSON API。",
    subtitle: "YouTube · 每 30 分鐘更新 ·",
    loading: "載入中…", updated_prefix: "更新於",
    s_ago: "{0} 秒前", m_ago: "{0} 分鐘前",
    nav_json: "JSON API", nav_rss: "RSS 訂閱", nav_history: "歷史封存", nav_source: "原始碼",
    views: "次觀看",
    no_data: "尚無資料，抓取任務尚未執行。",
    failed_load: "資料載入失敗：{0}",
    footer_via: "資料來源：YouTube Data API v3。",
    footer_feeds: "各國訂閱：",
  },
  "ja": { label: "日本語",
    title: "トレンドページ",
    description_meta: "各国の YouTube 急上昇動画を 30 分ごとに自動更新。RSS と JSON API を提供。",
    subtitle: "YouTube · 30 分ごとに更新 ·",
    loading: "読み込み中…", updated_prefix: "更新",
    s_ago: "{0}秒前", m_ago: "{0}分前",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "履歴", nav_source: "ソース",
    views: "回視聴",
    no_data: "データなし。スクレイパーは未実行です。",
    failed_load: "データ読み込みに失敗しました：{0}",
    footer_via: "YouTube Data API v3 提供。",
    footer_feeds: "国別フィード：",
  },
  "ko": { label: "한국어",
    title: "트렌딩 페이지",
    description_meta: "여러 지역의 YouTube 인기 동영상을 30분마다 자동 갱신. RSS 및 JSON API 제공.",
    subtitle: "YouTube · 30분마다 갱신 ·",
    loading: "불러오는 중…", updated_prefix: "업데이트",
    s_ago: "{0}초 전", m_ago: "{0}분 전",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "기록", nav_source: "소스",
    views: "회 시청",
    no_data: "데이터 없음. 스크레이퍼가 아직 실행되지 않았습니다.",
    failed_load: "데이터 로드 실패: {0}",
    footer_via: "데이터 출처: YouTube Data API v3.",
    footer_feeds: "국가별 피드:",
  },
  "es": { label: "Español",
    title: "Páginas de tendencias",
    description_meta: "Vídeos en tendencia de YouTube por región, actualizados cada 30 minutos. Incluye RSS y API JSON.",
    subtitle: "YouTube · actualizado cada 30 min ·",
    loading: "cargando…", updated_prefix: "actualizado",
    s_ago: "hace {0}s", m_ago: "hace {0}m",
    nav_json: "API JSON", nav_rss: "RSS", nav_history: "historial", nav_source: "código",
    views: "visualizaciones",
    no_data: "Aún no hay datos. El scraper no se ha ejecutado.",
    failed_load: "Error al cargar datos: {0}",
    footer_via: "Datos vía YouTube Data API v3.",
    footer_feeds: "Feeds por país:",
  },
  "hi": { label: "हिन्दी",
    title: "ट्रेंडिंग पेज",
    description_meta: "विभिन्न क्षेत्रों के YouTube ट्रेंडिंग वीडियो, हर 30 मिनट में अपडेट। RSS और JSON API भी।",
    subtitle: "YouTube · हर 30 मिनट में रिफ्रेश ·",
    loading: "लोड हो रहा है…", updated_prefix: "अपडेट",
    s_ago: "{0} सेकंड पहले", m_ago: "{0} मिनट पहले",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "इतिहास", nav_source: "स्रोत",
    views: "व्यू",
    no_data: "अभी कोई डेटा नहीं।",
    failed_load: "डेटा लोड विफल: {0}",
    footer_via: "डेटा: YouTube Data API v3 से।",
    footer_feeds: "देश-वार फ़ीड:",
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

const fmtNum = n => n >= 1e6 ? (n / 1e6).toFixed(1) + "M" : n >= 1e3 ? (n / 1e3).toFixed(1) + "K" : String(n ?? 0);
const fmtDuration = iso => {
  if (!iso) return "";
  const m = iso.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!m) return "";
  const h = +m[1] || 0, mn = +m[2] || 0, s = +m[3] || 0;
  const mm = String(mn).padStart(h ? 2 : 1, "0");
  const ss = String(s).padStart(2, "0");
  return h ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
};
const fmtAgo = iso => {
  const d = new Date(iso);
  const diff = (Date.now() - d) / 1000;
  if (diff < 60) return t("s_ago", Math.floor(diff));
  if (diff < 3600) return t("m_ago", Math.floor(diff / 60));
  return d.toLocaleString();
};

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function applyI18n() {
  document.documentElement.lang = HTML_LANG[lang] || "en";
  document.title = t("title");
  document.querySelectorAll("[data-i18n]").forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
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
    `<option value="${code}" ${code === lang ? "selected" : ""}>${v.label}</option>`
  ).join("");
  sel.addEventListener("change", () => {
    lang = sel.value;
    localStorage.setItem("lang", lang);
    applyI18n();
    state.rerender?.();
  });
}

function renderCards(items) {
  const grid = document.getElementById("grid");
  if (!items?.length) {
    grid.innerHTML = `<div class="empty">${escapeHtml(t("no_data"))}</div>`;
    return;
  }
  grid.innerHTML = items.map(it => `
    <article class="card">
      <a class="thumb" href="${it.url}" target="_blank" rel="noopener">
        ${it.thumbnail ? `<img loading="lazy" src="${it.thumbnail}" alt="">` : ""}
        <span class="rank">#${it.rank}</span>
      </a>
      <div class="body">
        <a class="title" href="${it.url}" target="_blank" rel="noopener">${escapeHtml(it.title || "")}</a>
        <div class="meta">
          <span>${escapeHtml(it.channel || "")}</span>
          <span>${fmtNum(it.views)} ${escapeHtml(t("views"))}</span>
          ${it.duration ? `<span>${fmtDuration(it.duration)}</span>` : ""}
        </div>
      </div>
    </article>
  `).join("");
}

function renderTabs(countries, current, onSelect) {
  const tabs = document.getElementById("tabs");
  tabs.innerHTML = countries.map(cc => `
    <button class="tab" role="tab" aria-selected="${cc === current}" data-cc="${cc}">${cc}</button>
  `).join("");
  tabs.querySelectorAll(".tab").forEach(el => {
    el.addEventListener("click", () => onSelect(el.dataset.cc));
  });
}

function renderFeeds(countries) {
  const el = document.getElementById("per-country-feeds");
  el.innerHTML = countries.map(cc =>
    `<a href="./data/feeds/${cc}.xml">${cc}</a><a href="./data/latest/${cc}.json">${cc}.json</a>`
  ).join(" · ");
}

function renderUpdated(iso) {
  document.getElementById("updated").textContent = `${t("updated_prefix")} ${fmtAgo(iso)}`;
}

const state = {};

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

  const countries = payload.countries || [];
  if (!countries.length) {
    document.getElementById("grid").innerHTML = `<div class="empty">${escapeHtml(t("no_data"))}</div>`;
    return;
  }

  renderUpdated(payload.updated_at);
  const initial = location.hash.replace("#", "") || countries[0];
  let current = countries.includes(initial) ? initial : countries[0];

  const select = cc => {
    current = cc;
    history.replaceState(null, "", `#${cc}`);
    renderTabs(countries, current, select);
    renderCards(payload.data[cc] || []);
  };

  state.rerender = () => {
    renderTabs(countries, current, select);
    renderFeeds(countries);
    renderCards(payload.data[current] || []);
    renderUpdated(payload.updated_at);
  };

  state.rerender();
})();
