/** Search page with autocomplete and results. */

function renderSearchPage() {
  const main = document.getElementById("mainContent");
  const div = document.createElement("div");
  div.className = "page active";
  div.id = "page-search";
  div.innerHTML = `
    <div class="search-container">
      <div class="search-input-wrapper">
        <input type="text" class="search-input" id="searchInput"
               placeholder="输入韩语或中文..."
               autocomplete="off" autocorrect="off" autocapitalize="off">
        <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </div>
      <div class="search-lang-toggle">
        <button class="lang-btn active" data-lang="kr" onclick="switchLang('kr')">한국어 → 中文</button>
        <button class="lang-btn" data-lang="zh" onclick="switchLang('zh')">中文 → 한국어</button>
      </div>
    </div>
    <div id="searchResults"></div>
    <div id="searchLoading" style="display:none" class="loading-text">
      <div class="spinner"></div> 查询中...
    </div>
  `;
  main.appendChild(div);

  // Search on input
  let debounceTimer;
  document.getElementById("searchInput").addEventListener("input", (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => doSearch(e.target.value.trim()), 300);
  });
}

let currentLang = "kr";

function switchLang(lang) {
  currentLang = lang;
  document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
  document.querySelector(`.lang-btn[data-lang="${lang}"]`).classList.add("active");
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
          <h3>未找到 "${query}"</h3>
          <p>试试其他关键词或切换搜索语言</p>
        </div>`;
      return;
    }

    resultsEl.innerHTML = data.results.map(w => `
      <div class="card" onclick="openSheet(${w.id})">
        <div>
          <span class="card-hangul">${escapeHtml(w.hangul)}</span>
          <span class="card-type">${typeLabel(w.type)}</span>
        </div>
        <div class="card-pron">[${escapeHtml(w.pronunciation)}]</div>
        <div class="card-meaning">${escapeHtml(w.chinese_meaning)}</div>
        ${w.is_irregular ? `<span style="display:inline-block;margin-top:4px;font-size:11px;padding:1px 6px;border-radius:12px;background:#FFF3CD;color:#856404">不规则: ${w.irregular_type}</span>` : ""}
      </div>
    `).join("");
  } catch (err) {
    loadingEl.style.display = "none";
    resultsEl.innerHTML = `<div class="empty-state"><h3>查询失败</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function typeLabel(type) {
  const map = {
    verb: "动词", adjective: "形容词", noun: "名词",
    adverb: "副词", determiner: "冠词", pronoun: "代词",
    numeral: "数词", interjection: "感叹词", particle: "助词",
  };
  return map[type] || type;
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
