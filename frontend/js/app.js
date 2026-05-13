/** Application shell: router, tab bar, sheet management. */

const PAGES = ["search", "sentence", "favorites", "settings"];
const TITLES = { search: "韩语助手", sentence: "句子分析", favorites: "收藏", settings: "设置" };
let currentPage = "search";
let sheetVisible = false;

// ---- Navigation ----
function navigateTo(page) {
  if (currentPage === page && !sheetVisible) return;

  // Hide all pages
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));

  // Show target page
  const el = document.getElementById(`page-${page}`);
  if (el) el.classList.add("active");

  // Update tab bar
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  const tabBtn = document.querySelector(`.tab-btn[data-page="${page}"]`);
  if (tabBtn) tabBtn.classList.add("active");

  // Update nav
  document.getElementById("navTitle").textContent = TITLES[page];
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
  document.documentElement.style.setProperty("--accent", accent || "#FF6B8A");
  document.documentElement.style.setProperty("--accent-light", hexToRgba(accent || "#FF6B8A", 0.15));
  document.documentElement.style.setProperty("--accent-dark", darkenColor(accent || "#FF6B8A", 0.15));
  document.querySelector('meta[name="theme-color"]').content = accent || "#FF6B8A";
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
async function initApp() {
  // Load settings
  const settings = await LocalCache.getSettings();
  applyTheme(settings.darkMode, settings.accentColor);

  // Render initial pages
  renderSearchPage();
  renderSentencePage();
  renderFavoritesPage();
  renderSettingsPage();

  // Default to search
  navigateTo("search");
}

document.addEventListener("DOMContentLoaded", initApp);
