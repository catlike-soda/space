/** Word detail bottom sheet with segmented control. */

let currentWord = null;
let currentSegment = "basic";

async function renderWordDetail(wordId) {
  const content = document.getElementById("sheetContent");
  content.innerHTML = '<div class="loading-text"><div class="spinner"></div> 加载中...</div>';

  try {
    const word = await API.getWord(wordId);
    currentWord = word;

    content.innerHTML = `
      <div style="text-align:center;padding:8px 0 16px">
        <div style="font-family:var(--font-korean);font-size:32px;font-weight:700;color:var(--text-primary)">
          ${escapeHtml(word.hangul)}
        </div>
        <div style="font-size:14px;color:var(--text-secondary);margin-top:4px">
          [${escapeHtml(word.pronunciation)}]
          ${word.hanja ? ' <span style="color:var(--text-tertiary)">('+escapeHtml(word.hanja)+')</span>' : ''}
        </div>
        <div style="margin-top:8px">
          <span class="card-type">${typeLabel(word.type)}</span>
          ${word.level ? `<span style="display:inline-block;margin-left:6px;font-size:11px;padding:2px 8px;border-radius:12px;background:var(--text-tertiary);color:white">${levelLabel(word.level)}</span>` : ""}
          ${word.is_irregular ? `<span style="display:inline-block;margin-left:6px;font-size:11px;padding:2px 8px;border-radius:12px;background:#FFF3CD;color:#856404">不规则${word.irregular_type}</span>` : ""}
        </div>
        <div style="font-size:18px;color:var(--text-primary);margin-top:12px;font-weight:500">
          ${escapeHtml(word.chinese_meaning)}
        </div>
        ${word.definition_kr ? `<div style="font-size:14px;color:var(--text-secondary);margin-top:4px">${escapeHtml(word.definition_kr)}</div>` : ""}
      </div>

      <div style="display:flex;gap:8px;justify-content:center;padding-bottom:8px">
        <button onclick="TTS.speak('${escapeHtml(word.hangul)}')" style="display:flex;align-items:center;gap:4px;padding:8px 16px;border:none;border-radius:var(--radius-pill);background:var(--bg-input);color:var(--accent);font-size:14px;font-weight:500;cursor:pointer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
          朗读
        </button>
        <button id="favBtn" onclick="toggleFavorite(${word.id})" style="display:flex;align-items:center;gap:4px;padding:8px 16px;border:none;border-radius:var(--radius-pill);background:var(--bg-input);color:var(--text-secondary);font-size:14px;font-weight:500;cursor:pointer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
          收藏
        </button>
      </div>

      <div class="segmented-control">
        <button class="segment-btn active" data-seg="basic" onclick="switchSegment('basic')">基本信息</button>
        ${word.type === 'verb' || word.type === 'adjective' ? '<button class="segment-btn" data-seg="conj" onclick="switchSegment(\'conj\')">活用形</button>' : ''}
        <button class="segment-btn" data-seg="sent" onclick="switchSegment('sent')">例句</button>
        <button class="segment-btn" data-seg="related" onclick="switchSegment('related')">关联词</button>
      </div>

      <div id="segmentContent"></div>
    `;

    switchSegment("basic");
  } catch (err) {
    content.innerHTML = `<div class="empty-state"><h3>加载失败</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}

function switchSegment(seg) {
  currentSegment = seg;
  document.querySelectorAll(".segment-btn").forEach(b => b.classList.remove("active"));
  document.querySelector(`.segment-btn[data-seg="${seg}"]`)?.classList.add("active");

  const el = document.getElementById("segmentContent");
  if (!el) return;

  switch (seg) {
    case "basic": renderBasicInfo(el); break;
    case "conj": renderConjugationSegment(el); break;
    case "sent": renderSentences(el); break;
    case "related": renderRelated(el); break;
  }
}

function renderBasicInfo(el) {
  const w = currentWord;
  el.innerHTML = `
    <div class="card">
      <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">词条信息</div>
      <div style="display:grid;grid-template-columns:auto 1fr;gap:8px 16px;font-size:14px">
        <span style="color:var(--text-secondary)">韩文</span><span style="font-family:var(--font-korean)">${escapeHtml(w.hangul)}</span>
        <span style="color:var(--text-secondary)">发音</span><span>[${escapeHtml(w.pronunciation)}]</span>
        ${w.hanja ? `<span style="color:var(--text-secondary)">汉字</span><span>${escapeHtml(w.hanja)}</span>` : ""}
        <span style="color:var(--text-secondary)">词性</span><span>${typeLabel(w.type)}</span>
        <span style="color:var(--text-secondary)">等级</span><span>${levelLabel(w.level)}</span>
        ${w.is_irregular ? `<span style="color:var(--text-secondary)">不规则</span><span>${w.irregular_type} 不规则</span>` : ""}
        ${w.stem ? `<span style="color:var(--text-secondary)">词干</span><span style="font-family:var(--font-korean)">${escapeHtml(w.stem)}</span>` : ""}
      </div>
    </div>
    ${w.definition_en ? `<div class="card"><div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px">英文释义</div><div style="font-size:14px">${escapeHtml(w.definition_en)}</div></div>` : ""}
  `;
}

async function renderConjugationSegment(el) {
  el.innerHTML = '<div class="loading-text"><div class="spinner"></div> 加载活用形...</div>';
  try {
    const data = await API.getConjugations(currentWord.id);
    el.innerHTML = ConjugationTable.render(data.conjugations, data.type, data.is_irregular);
  } catch (err) {
    el.innerHTML = `<div class="empty-state"><p>加载失败: ${escapeHtml(err.message)}</p></div>`;
  }
}

function renderSentences(el) {
  const sentences = currentWord.example_sentences || [];
  if (!sentences.length) {
    el.innerHTML = '<div class="empty-state"><p>暂无例句</p></div>';
    return;
  }
  el.innerHTML = sentences.map(s => `
    <div class="grammar-card" onclick="TTS.speak('${escapeHtml(s.sentence_kr)}')">
      <div style="font-family:var(--font-korean);font-size:16px;margin-bottom:4px">${escapeHtml(s.sentence_kr)}</div>
      <div style="font-size:14px;color:var(--text-secondary)">${escapeHtml(s.sentence_zh)}</div>
    </div>
  `).join("");
}

function renderRelated(el) {
  const related = currentWord.related_words || [];
  if (!related.length) {
    el.innerHTML = '<div class="empty-state"><p>暂无关联词</p></div>';
    return;
  }
  el.innerHTML = related.map(r => {
    const w = r.word;
    if (!w) return "";
    return `
      <div class="card" onclick="openSheet(${w.id})">
        <div>
          <span class="card-hangul">${escapeHtml(w.hangul)}</span>
          <span class="card-type">${typeLabel(w.type)}</span>
          <span style="font-size:11px;color:var(--text-tertiary);margin-left:6px">${relLabel(r.relation_type)}</span>
        </div>
        <div class="card-meaning">${escapeHtml(w.chinese_meaning)}</div>
      </div>`;
  }).join("");
}

async function toggleFavorite(wordId) {
  const word = currentWord;
  const isFav = await LocalCache.toggleFavorite(word);
  const btn = document.getElementById("favBtn");
  if (btn) {
    btn.style.color = isFav ? "#FF3B30" : "var(--text-secondary)";
  }
  showToast(isFav ? "已收藏" : "已取消收藏");
}

function levelLabel(level) {
  const map = { beginner: "初级", intermediate: "中级", advanced: "高级" };
  return map[level] || level || "";
}

function relLabel(type) {
  const map = { synonym: "同义", antonym: "反义", derived: "派生", compound: "复合" };
  return map[type] || type;
}
