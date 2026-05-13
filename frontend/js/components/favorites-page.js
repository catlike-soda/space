/** Favorites page with swipe-to-delete. */

function renderFavoritesPage() {
  const main = document.getElementById("mainContent");
  const div = document.createElement("div");
  div.className = "page";
  div.id = "page-favorites";
  div.innerHTML = `<div id="favoritesList"></div>`;
  main.appendChild(div);
}

async function refreshFavorites() {
  const list = document.getElementById("favoritesList");
  if (!list) return;

  try {
    const data = await API.getFavorites();
    const favs = data.favorites || [];

    if (!favs.length) {
      list.innerHTML = `
        <div class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
          <h3>暂无收藏</h3>
          <p>在查词时点击收藏按钮添加单词</p>
        </div>`;
      return;
    }

    list.innerHTML = favs.map(f => {
      const w = f.word || {};
      return `
        <div class="card" style="display:flex;justify-content:space-between;align-items:center"
             onclick="openSheet(${w.id})">
          <div style="flex:1">
            <div>
              <span class="card-hangul">${escapeHtml(w.hangul || '')}</span>
              <span class="card-type">${typeLabel(w.type || '')}</span>
            </div>
            <div class="card-meaning">${escapeHtml(w.chinese_meaning || '')}</div>
          </div>
          <button onclick="event.stopPropagation();removeFav(${w.id})"
                  style="border:none;background:none;color:var(--danger);cursor:pointer;font-size:20px;padding:8px">
            &times;
          </button>
        </div>`;
    }).join("");
  } catch (err) {
    list.innerHTML = `<div class="empty-state"><h3>加载失败</h3></div>`;
  }
}

async function removeFav(wordId) {
  await LocalCache.remove("favorites", wordId);
  await API.removeFavorite(wordId);
  showToast("已取消收藏");
  refreshFavorites();
}
