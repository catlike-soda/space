/** Settings page: dark mode, accent color, about. */

const ACCENT_COLORS = [
  { name: "暖粉", color: "#FF6B8A" },
  { name: "珊瑚", color: "#FF6B6B" },
  { name: "天空", color: "#4A90D9" },
  { name: "薄荷", color: "#34C759" },
  { name: "橙黄", color: "#FF9500" },
  { name: "紫色", color: "#AF52DE" },
  { name: "靛蓝", color: "#5856D6" },
  { name: "棕褐", color: "#A2845E" },
];

let _darkMode = false;
let _accentColor = "#FF6B8A";

function renderSettingsPage() {
  const main = document.getElementById("mainContent");
  const div = document.createElement("div");
  div.className = "page";
  div.id = "page-settings";
  div.innerHTML = `
    <div class="settings-group">
      <div class="settings-group-title">显示</div>
      <div class="settings-row">
        <span class="settings-label">暗黑模式</span>
        <button class="toggle-switch" id="darkToggle" onclick="toggleDarkMode()"></button>
      </div>
      <div class="settings-row">
        <span class="settings-label">主题色</span>
      </div>
      <div class="settings-row" style="flex-wrap:wrap">
        <div class="accent-picker" id="accentPicker">
          ${ACCENT_COLORS.map((c, i) => `
            <div class="accent-dot" style="background:${c.color}" data-color="${c.color}"
                 onclick="setAccentColor('${c.color}')" title="${c.name}"></div>
          `).join("")}
        </div>
      </div>
    </div>
    <div class="settings-group">
      <div class="settings-group-title">关于</div>
      <div class="settings-row">
        <span class="settings-label">版本</span>
        <span style="color:var(--text-secondary)">1.0.0</span>
      </div>
      <div class="settings-row">
        <span class="settings-label">数据来源</span>
        <span style="color:var(--text-secondary)">TOPIK词汇 + AI分析</span>
      </div>
    </div>
  `;
  main.appendChild(div);

  // Init
  loadSettings();
}

async function loadSettings() {
  const s = await LocalCache.getSettings();
  _darkMode = s.darkMode;
  _accentColor = s.accentColor;

  updateDarkToggle();
  updateAccentPicker();
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
  if (_darkMode) {
    btn.classList.add("on");
  } else {
    btn.classList.remove("on");
  }
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
