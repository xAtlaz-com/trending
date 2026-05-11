const BASE = (location.pathname.endsWith("/") ? location.pathname : location.pathname.replace(/[^/]+$/, ""));
const DATA_URL = `./data/latest.json?t=${Date.now()}`;

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
const fmtUpdated = iso => {
  const d = new Date(iso);
  const diff = (Date.now() - d) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return d.toLocaleString();
};

function renderCards(items) {
  const grid = document.getElementById("grid");
  if (!items?.length) {
    grid.innerHTML = `<div class="empty">No data yet. The scraper hasn't run.</div>`;
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
          <span>${fmtNum(it.views)} views</span>
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

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

(async function init() {
  const repoLink = document.getElementById("repo-link");
  if (location.hostname.endsWith("github.io")) {
    const [user, repo] = [location.hostname.split(".")[0], location.pathname.split("/")[1]];
    if (user && repo) repoLink.href = `https://github.com/${user}/${repo}`;
  }

  let payload;
  try {
    payload = await fetch(DATA_URL).then(r => r.json());
  } catch (e) {
    document.getElementById("grid").innerHTML = `<div class="empty">Failed to load data: ${e.message}</div>`;
    return;
  }

  document.getElementById("updated").textContent = `updated ${fmtUpdated(payload.updated_at)}`;
  const countries = payload.countries || [];
  if (!countries.length) {
    document.getElementById("grid").innerHTML = `<div class="empty">No data yet.</div>`;
    return;
  }

  const initial = location.hash.replace("#", "") || countries[0];
  let current = countries.includes(initial) ? initial : countries[0];

  const select = cc => {
    current = cc;
    history.replaceState(null, "", `#${cc}`);
    renderTabs(countries, current, select);
    renderCards(payload.data[cc] || []);
  };

  renderTabs(countries, current, select);
  renderFeeds(countries);
  renderCards(payload.data[current] || []);
})();
