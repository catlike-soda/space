/** Word detail bottom sheet with segmented control. */

let currentWord = null;
let currentSegment = "basic";

async function renderWordDetail(wordId) {
  const content = document.getElementById("sheetContent");
  content.innerHTML = '<div class="loading-text"><div class="spinner"></div> ' + t('word_loading') + '</div>';

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
          <span class="card-type">${t('type_' + word.type) || word.type}</span>
          ${word.level ? `<span style="display:inline-block;margin-left:6px;font-size:11px;padding:2px 8px;border-radius:12px;background:var(--text-tertiary);color:white">${levelLabel(word.level)}</span>` : ""}
          ${word.is_irregular ? `<span style="display:inline-block;margin-left:6px;font-size:11px;padding:2px 8px;border-radius:12px;background:#FFF3CD;color:#856404">${t('word_irregular')}${word.irregular_type}</span>` : ""}
        </div>
        <div style="font-size:18px;color:var(--text-primary);margin-top:12px;font-weight:500">
          ${escapeHtml(word.meaning_for_ui || word.chinese_meaning)}
        </div>
        ${word.definition_kr ? `<div style="font-size:14px;color:var(--text-secondary);margin-top:4px">${escapeHtml(word.definition_kr)}</div>` : ""}
      </div>

      <div style="display:flex;gap:8px;justify-content:center;padding-bottom:8px">
        <button onclick="TTS.speak('${escapeHtml(word.hangul)}')" style="display:flex;align-items:center;gap:4px;padding:8px 16px;border:none;border-radius:var(--radius-pill);background:var(--bg-input);color:var(--accent);font-size:14px;font-weight:500;cursor:pointer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
          ${t('word_tts')}
        </button>
        <button id="favBtn" onclick="toggleFavorite(${word.id})" style="display:flex;align-items:center;gap:4px;padding:8px 16px;border:none;border-radius:var(--radius-pill);background:var(--bg-input);color:var(--text-secondary);font-size:14px;font-weight:500;cursor:pointer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
          ${t('word_fav')}
        </button>
      </div>

      <div class="segmented-control">
        <button class="segment-btn active" data-seg="basic" onclick="switchSegment('basic')">${t('word_seg_basic')}</button>
        ${word.type === 'verb' || word.type === 'adjective' ? '<button class="segment-btn" data-seg="conj" onclick="switchSegment(\'conj\')">' + t('word_seg_conj') + '</button>' : ''}
        <button class="segment-btn" data-seg="sent" onclick="switchSegment('sent')">${t('word_seg_sent')}</button>
        <button class="segment-btn" data-seg="related" onclick="switchSegment('related')">${t('word_seg_related')}</button>
      </div>

      <div id="segmentContent"></div>
    `;

    switchSegment("basic");
  } catch (err) {
    content.innerHTML = `<div class="empty-state"><h3>${t('word_load_fail')}</h3><p>${escapeHtml(err.message)}</p></div>`;
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
      <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">${t('word_info_title')}</div>
      <div style="display:grid;grid-template-columns:auto 1fr;gap:8px 16px;font-size:14px">
        <span style="color:var(--text-secondary)">${t('word_info_hangul')}</span><span style="font-family:var(--font-korean)">${escapeHtml(w.hangul)}</span>
        <span style="color:var(--text-secondary)">${t('word_info_pron')}</span><span>[${escapeHtml(w.pronunciation)}]</span>
        ${w.hanja ? `<span style="color:var(--text-secondary)">${t('word_info_hanja')}</span><span>${escapeHtml(w.hanja)}</span>` : ""}
        <span style="color:var(--text-secondary)">${t('word_info_type')}</span><span>${t('type_' + w.type) || w.type}</span>
        <span style="color:var(--text-secondary)">${t('word_info_level')}</span><span>${levelLabel(w.level)}</span>
        ${w.is_irregular ? `<span style="color:var(--text-secondary)">${t('word_info_irregular')}</span><span>${w.irregular_type}</span>` : ""}
        ${w.stem ? `<span style="color:var(--text-secondary)">${t('word_info_stem')}</span><span style="font-family:var(--font-korean)">${escapeHtml(w.stem)}</span>` : ""}
      </div>
    </div>
    ${w.definition_en ? `<div class="card"><div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px">${t('word_en_def')}</div><div style="font-size:14px">${escapeHtml(w.definition_en)}</div></div>` : ""}
  `;
}

async function renderConjugationSegment(el) {
  el.innerHTML = '<div class="loading-text"><div class="spinner"></div> ' + t('word_conj_loading') + '</div>';
  try {
    const data = await API.getConjugations(currentWord.id);
    el.innerHTML = ConjugationTable.render(data.conjugations, data.type, data.is_irregular);
  } catch (err) {
    el.innerHTML = `<div class="empty-state"><p>${t('word_load_fail')}: ${escapeHtml(err.message)}</p></div>`;
  }
}

function renderSentences(el) {
  const sentences = currentWord.example_sentences || [];
  if (!sentences.length) {
    el.innerHTML = `<div class="empty-state"><p>${t('word_no_sentences')}</p></div>`;
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
    el.innerHTML = `<div class="empty-state"><p>${t('word_no_related')}</p></div>`;
    return;
  }
  el.innerHTML = related.map(r => {
    const w = r.word;
    if (!w) return "";
    return `
      <div class="card" onclick="openSheet(${w.id})">
        <div>
          <span class="card-hangul">${escapeHtml(w.hangul)}</span>
          <span class="card-type">${t('type_' + w.type) || w.type}</span>
          <span style="font-size:11px;color:var(--text-tertiary);margin-left:6px">${t('rel_' + r.relation_type) || r.relation_type}</span>
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
  showToast(isFav ? t('word_faved') : t('word_unfaved'));
}
