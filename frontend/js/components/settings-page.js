/** Settings page: dark mode, accent color, language, about. */

const ACCENT_COLORS = [
  { name: "accent_warm_pink", color: "#FF7BA6" },
  { name: "accent_coral", color: "#FF8A80" },
  { name: "accent_peach", color: "#FFB997" },
  { name: "accent_sky", color: "#89C4F4" },
  { name: "accent_mint", color: "#7BC8A4" },
  { name: "accent_lavender", color: "#C3A6D8" },
  { name: "accent_butter", color: "#FFE08A" },
  { name: "accent_rose", color: "#F8BBD0" },
];

const LANGUAGES = [
  { code: "ja", label: "日本語" },
  { code: "zh", label: "中文" },
];

let _darkMode = true;
let _accentColor = "#FF6B8A";

function renderSettingsPage() {
  const main = document.getElementById("mainContent");
  const div = document.createElement("div");
  div.className = "page";
  div.id = "page-settings";
  div.innerHTML = `
    <div class="settings-group">
      <div class="settings-group-title">${t('settings_display')}</div>
      <div class="settings-row">
        <span class="settings-label">${t('settings_dark_mode')}</span>
        <button class="toggle-switch" id="darkToggle" onclick="toggleDarkMode()"></button>
      </div>
      <div class="settings-row">
        <span class="settings-label">${t('settings_accent')}</span>
      </div>
      <div class="settings-row" style="flex-wrap:wrap">
        <div class="accent-picker" id="accentPicker">
          ${ACCENT_COLORS.map(c => `
            <div class="accent-dot" style="background:${c.color}" data-color="${c.color}"
                 onclick="setAccentColor('${c.color}')" title="${t(c.name)}"></div>
          `).join("")}
        </div>
      </div>
      <div class="settings-row">
        <span class="settings-label">${t('settings_language')}</span>
        <select id="langSelect" onchange="changeLanguage(this.value)" style="font-size:14px;padding:6px 12px;border-radius:8px;border:1px solid var(--separator);background:var(--bg-input);color:var(--text-primary)">
          ${LANGUAGES.map(l => `<option value="${l.code}" ${getLocale() === l.code ? 'selected' : ''}>${l.label}</option>`).join("")}
        </select>
      </div>
    </div>
    <div class="settings-group">
      <div class="settings-group-title">${t('settings_about')}</div>
      <div class="settings-row">
        <span class="settings-label">${t('settings_version')}</span>
        <span style="color:var(--text-secondary)">1.0.0</span>
      </div>
      <div class="settings-row">
        <span class="settings-label">${t('settings_data_source')}</span>
        <span style="color:var(--text-secondary)">${t('settings_data_value')}</span>
      </div>
    </div>
  `;
  main.appendChild(div);

  loadSettings();
}

async function loadSettings() {
  const s = await LocalCache.getSettings();
  _darkMode = s.darkMode;
  _accentColor = s.accentColor;

  updateDarkToggle();
  updateAccentPicker();

  // Ensure initial toggle state matches
  const toggle = document.getElementById("darkToggle");
  if (toggle) {
    if (_darkMode) toggle.classList.add("on");
    else toggle.classList.remove("on");
  }
}

function toggleDarkMode() {
  _darkMode = !_darkMode;
  applyTheme(_darkMode, _accentColor);
  LocalCache.saveSetting("darkMode", _darkMode);
  updateDarkToggle();
}

function updateDarkToggle() {
  const btn = document.getElementById("darkToggle");
  if (!btn) return;
  if (_darkMode) btn.classList.add("on");
  else btn.classList.remove("on");
}

function setAccentColor(color) {
  _accentColor = color;
  applyTheme(_darkMode, _accentColor);
  LocalCache.saveSetting("accentColor", _accentColor);
  updateAccentPicker();
}

function updateAccentPicker() {
  document.querySelectorAll(".accent-dot").forEach(d => {
    d.classList.remove("active");
    if (d.dataset.color === _accentColor) d.classList.add("active");
  });
}

function changeLanguage(loc) {
  setLocale(loc);
  // Reset search direction
  currentLang = getDefaultSearchLang();
  // Re-render all pages with new locale
  const main = document.getElementById("mainContent");
  main.innerHTML = "";
  document.title = t("app_name");
  document.querySelector('meta[name="apple-mobile-web-app-title"]').content = t("app_name");
  // Update tab labels
  document.querySelector(".tab-btn[data-page='search'] span").textContent = t("tab_search");
  document.querySelector(".tab-btn[data-page='sentence'] span").textContent = t("tab_sentence");
  document.querySelector(".tab-btn[data-page='favorites'] span").textContent = t("tab_favorites");
  document.querySelector(".tab-btn[data-page='settings'] span").textContent = t("tab_settings");
  // Render all pages fresh
  renderSearchPage();
  renderSentencePage();
  renderFavoritesPage();
  renderSettingsPage();
  // Navigate to current page (reset first to bypass early-return)
  const wasPage = currentPage;
  currentPage = "";
  navigateTo(wasPage);
}
