/** Application shell: router, tab bar, sheet management. */

const PAGES = ["search", "sentence", "favorites", "settings"];
let currentPage = "search";
let sheetVisible = false;

function getTitles() {
  return {
    search: t("title_search"),
    sentence: t("title_sentence"),
    favorites: t("title_favorites"),
    settings: t("title_settings"),
  };
}

// ---- Navigation ----
function navigateTo(page) {
  if (currentPage === page && !sheetVisible) return;

  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));

  const el = document.getElementById(`page-${page}`);
  if (el) el.classList.add("active");

  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  const tabBtn = document.querySelector(`.tab-btn[data-page="${page}"]`);
  if (tabBtn) tabBtn.classList.add("active");

  // Favorites is dynamic with async refresh
  if (page === "favorites") refreshFavorites();

  const titles = getTitles();
  document.getElementById("navTitle").textContent = titles[page];
  document.getElementById("navBack").style.display = (page === "search") ? "none" : "inline-flex";

  currentPage = page;
  closeSheet();
}

// ---- Bottom Sheet ----
function openSheet(wordId) {
  document.getElementById("sheetOverlay").classList.add("active");
  document.getElementById("bottomSheet").classList.add("active");
  sheetVisible = true;
  renderWordDetail(wordId);
}

function closeSheet() {
  document.getElementById("sheetOverlay").classList.remove("active");
  document.getElementById("bottomSheet").classList.remove("active");
  sheetVisible = false;
}

// ---- Toast ----
function showToast(msg, duration = 2000) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.add("show");
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => toast.classList.remove("show"), duration);
}

// ---- Theme ----
function applyTheme(dark, accent) {
  document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
  document.documentElement.style.setProperty("--accent", accent || "#2DD4BF");
  document.documentElement.style.setProperty("--accent-light", hexToRgba(accent || "#2DD4BF", 0.15));
  document.documentElement.style.setProperty("--accent-dark", darkenColor(accent || "#2DD4BF", 0.15));
  document.querySelector('meta[name="theme-color"]').content = dark ? "#000000" : (accent || "#2DD4BF");
}

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function darkenColor(hex, amount) {
  const r = Math.max(0, parseInt(hex.slice(1, 3), 16) * (1 - amount));
  const g = Math.max(0, parseInt(hex.slice(3, 5), 16) * (1 - amount));
  const b = Math.max(0, parseInt(hex.slice(5, 7), 16) * (1 - amount));
  return `rgb(${Math.round(r)},${Math.round(g)},${Math.round(b)})`;
}

// ---- Init ----
const DEFAULT_ACCENT = "#2DD4BF";

async function initApp() {
  // Load locale first, then settings
  await loadLocale();
  const settings = await LocalCache.getSettings();

  // Migrate old pink accent to new teal default
  if (settings.accentColor === "#FF6B8A" || settings.accentColor === "#FF7BA6" || settings.accentColor === "#FF5C8A") {
    settings.accentColor = DEFAULT_ACCENT;
    await LocalCache.saveSetting("accentColor", DEFAULT_ACCENT);
  }

  applyTheme(settings.darkMode, settings.accentColor);

  // Update tab bar labels
  document.querySelector(".tab-btn[data-page='search'] span").textContent = t("tab_search");
  document.querySelector(".tab-btn[data-page='sentence'] span").textContent = t("tab_sentence");
  document.querySelector(".tab-btn[data-page='favorites'] span").textContent = t("tab_favorites");
  document.querySelector(".tab-btn[data-page='settings'] span").textContent = t("tab_settings");

  // Render pages
  renderSearchPage();
  renderSentencePage();
  renderFavoritesPage();
  renderSettingsPage();

  navigateTo("search");
}

document.addEventListener("DOMContentLoaded", initApp);
