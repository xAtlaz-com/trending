// Static pages render their own HTML and JSON-LD; this script is a
// progressive-enhancement layer that only translates the UI chrome
// (header labels, footer hints, nav links) using a stored or detected
// browser language. No data fetching, no DOM construction.

const I18N = {
  "en": { label: "English",
    title: "Trending Pages",
    description_meta: "YouTube / GitHub / V2EX / 微博 / 知乎 / 抖音 / 头条 trending, refreshed every 30 minutes. RSS + JSON API.",
    subtitle: "Refreshed every 30 min ·",
    loading: "loading…", updated_prefix: "updated",
    s_ago: "{0}s ago", m_ago: "{0}m ago",
    nav_json: "latest.json", nav_rss: "RSS", nav_history: "history", nav_source: "source",
    footer_feeds: "Per-source feeds:",
  },
  "zh-Hans": { label: "简体中文",
    title: "趋势榜单",
    description_meta: "覆盖 YouTube / GitHub / V2EX / 微博 / 知乎 / 抖音 / 头条 的实时榜单，每 30 分钟自动更新。",
    subtitle: "每 30 分钟刷新 ·",
    loading: "加载中…", updated_prefix: "更新于",
    s_ago: "{0} 秒前", m_ago: "{0} 分钟前",
    nav_json: "JSON API", nav_rss: "RSS 订阅", nav_history: "历史归档", nav_source: "源码",
    footer_feeds: "分源订阅：",
  },
  "zh-Hant": { label: "繁體中文",
    title: "熱門趨勢",
    description_meta: "涵蓋 YouTube / GitHub / V2EX / 微博 / 知乎 / 抖音 / 頭條 即時榜單，每 30 分鐘自動更新。",
    subtitle: "每 30 分鐘更新 ·",
    loading: "載入中…", updated_prefix: "更新於",
    s_ago: "{0} 秒前", m_ago: "{0} 分鐘前",
    nav_json: "JSON API", nav_rss: "RSS 訂閱", nav_history: "歷史封存", nav_source: "原始碼",
    footer_feeds: "分源訂閱：",
  },
  "ja": { label: "日本語",
    title: "トレンドページ",
    subtitle: "30 分ごとに更新 ·",
    updated_prefix: "更新",
    s_ago: "{0}秒前", m_ago: "{0}分前",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "履歴", nav_source: "ソース",
    footer_feeds: "ソース別フィード：",
  },
  "ko": { label: "한국어",
    title: "트렌딩 페이지",
    subtitle: "30분마다 갱신 ·",
    updated_prefix: "업데이트",
    s_ago: "{0}초 전", m_ago: "{0}분 전",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "기록", nav_source: "소스",
    footer_feeds: "소스별 피드:",
  },
  "es": { label: "Español",
    title: "Páginas de tendencias",
    subtitle: "Actualizado cada 30 min ·",
    updated_prefix: "actualizado",
    s_ago: "hace {0}s", m_ago: "hace {0}m",
    nav_json: "API JSON", nav_rss: "RSS", nav_history: "historial", nav_source: "código",
    footer_feeds: "Feeds por fuente:",
  },
  "hi": { label: "हिन्दी",
    title: "ट्रेंडिंग पेज",
    subtitle: "हर 30 मिनट में रिफ्रेश ·",
    updated_prefix: "अपडेट",
    s_ago: "{0} सेकंड पहले", m_ago: "{0} मिनट पहले",
    nav_json: "JSON API", nav_rss: "RSS", nav_history: "इतिहास", nav_source: "स्रोत",
    footer_feeds: "स्रोत-वार फ़ीड:",
  },
};
const HTML_LANG = { "en": "en", "zh-Hans": "zh-Hans", "zh-Hant": "zh-Hant", "ja": "ja", "ko": "ko", "es": "es", "hi": "hi" };

function detectLang() {
  try {
    const stored = localStorage.getItem("lang");
    if (stored && I18N[stored]) return stored;
  } catch (e) {}
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

function applyI18n() {
  document.documentElement.lang = HTML_LANG[lang] || "en";
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-attr]").forEach(el => {
    el.dataset.i18nAttr.split(",").forEach(pair => {
      const [attr, key] = pair.split(":");
      el.setAttribute(attr, t(key));
    });
  });
  refreshUpdated();
}

function renderLangSelect() {
  const sel = document.getElementById("lang-select");
  if (!sel) return;
  sel.innerHTML = Object.entries(I18N).map(([code, v]) =>
    `<option value="${code}" ${code === lang ? "selected" : ""}>${v.label}</option>`).join("");
  sel.addEventListener("change", () => {
    lang = sel.value;
    try { localStorage.setItem("lang", lang); } catch (e) {}
    applyI18n();
  });
}

// Re-format the "updated Xm ago" string in the active language if it was
// rendered server-side with an ISO timestamp inside data-updated-at.
function refreshUpdated() {
  const el = document.getElementById("updated");
  if (!el) return;
  const iso = el.dataset.updatedAt;
  if (!iso) return;
  const d = new Date(iso);
  if (isNaN(d)) return;
  const diff = (Date.now() - d.getTime()) / 1000;
  let text;
  if (diff < 60) text = t("s_ago", Math.floor(diff));
  else if (diff < 3600) text = t("m_ago", Math.floor(diff / 60));
  else text = d.toLocaleString();
  el.textContent = `${t("updated_prefix")} ${text}`;
}

(function init() {
  renderLangSelect();
  applyI18n();
})();
