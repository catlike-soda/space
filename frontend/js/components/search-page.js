/** Search page with autocomplete and results. */

let currentLang = getDefaultSearchLang();

function renderSearchPage() {
  const main = document.getElementById("mainContent");
  const div = document.createElement("div");
  div.className = "page active";
  div.id = "page-search";
  div.innerHTML = `
    <div class="search-container">
      <div class="search-input-wrapper">
        <input type="text" class="search-input" id="searchInput"
               placeholder="${t('search_placeholder')}"
               autocomplete="off" autocorrect="off" autocapitalize="off">
        <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </div>
      <div class="search-lang-toggle">
        ${getLocale() === 'ja' ? `
          <button class="lang-btn" id="langBtnKrJa" data-lang="kr_ja" onclick="switchLang('kr_ja')">${t('search_btn_kr_ja')}</button>
          <button class="lang-btn" id="langBtnJa" data-lang="ja" onclick="switchLang('ja')">${t('search_btn_ja')}</button>
        ` : `
          <button class="lang-btn" id="langBtnKr" data-lang="kr" onclick="switchLang('kr')">${t('search_btn_kr')}</button>
          <button class="lang-btn" id="langBtnZh" data-lang="zh" onclick="switchLang('zh')">${t('search_btn_zh')}</button>
        `}
      </div>
    </div>
    <div id="searchResults"></div>
    <div id="searchLoading" style="display:none" class="loading-text">
      <div class="spinner"></div> ${t('search_loading')}
    </div>
  `;
  main.appendChild(div);

  // Set initial active lang button
  highlightLangBtn(currentLang);

  // Search on input
  let debounceTimer;
  document.getElementById("searchInput").addEventListener("input", (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => doSearch(e.target.value.trim()), 300);
  });
}

function highlightLangBtn(lang) {
  document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
  const btn = document.querySelector(`.lang-btn[data-lang="${lang}"]`);
  if (btn) btn.classList.add("active");
}

function switchLang(lang) {
  currentLang = lang;
  highlightLangBtn(lang);
  const query = document.getElementById("searchInput").value.trim();
  if (query) doSearch(query);
}

async function doSearch(query) {
  const resultsEl = document.getElementById("searchResults");
  const loadingEl = document.getElementById("searchLoading");

  if (!query || query.length < 1) {
    resultsEl.innerHTML = "";
    return;
  }

  loadingEl.style.display = "block";
  resultsEl.innerHTML = "";

  try {
    const data = await API.search(query, currentLang);
    loadingEl.style.display = "none";

    if (!data.results || data.results.length === 0) {
      resultsEl.innerHTML = `
        <div class="empty-state">
          <h3>${t('search_no_results').replace('{query}', escapeHtml(query))}</h3>
          <p>${t('search_no_hint')}</p>
        </div>`;
      return;
    }

    resultsEl.innerHTML = data.results.map(w => `
      <div class="card" onclick="openSheet(${w.id})">
        <div>
          <span class="card-hangul">${escapeHtml(w.hangul)}</span>
          <span class="card-type">${t('type_' + w.type) || typeLabel(w.type)}</span>
        </div>
        <div class="card-pron">[${escapeHtml(w.pronunciation)}]</div>
        <div class="card-meaning">
          ${escapeHtml(w.meaning_for_ui || w.chinese_meaning || '')}
        </div>
        ${w.is_irregular ? `<span style="display:inline-block;margin-top:4px;font-size:11px;padding:1px 6px;border-radius:12px;background:#FFF3CD;color:#856404">${t('search_irregular')}: ${w.irregular_type}</span>` : ""}
      </div>
    `).join("");
  } catch (err) {
    loadingEl.style.display = "none";
    resultsEl.innerHTML = `<div class="empty-state"><h3>${t('search_error')}</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function typeLabel(type) {
  return t('type_' + type) || type;
}

function levelLabel(level) {
  return t('level_' + level) || level || "";
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
