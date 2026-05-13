/** Sentence analysis page. */

function renderSentencePage() {
  const main = document.getElementById("mainContent");
  const div = document.createElement("div");
  div.className = "page";
  div.id = "page-sentence";
  div.innerHTML = `
    <textarea class="sentence-input" id="sentenceInput"
              placeholder="${t('sent_placeholder')}"></textarea>
    <button class="analyze-btn" id="analyzeBtn" onclick="analyzeSentence()">
      ${t('sent_analyze_btn')}
    </button>
    <div id="analysisResult"></div>
    <div id="analysisLoading" style="display:none" class="loading-text">
      <div class="spinner"></div> ${t('sent_analyzing')}
    </div>
  `;
  main.appendChild(div);
}

async function analyzeSentence() {
  const input = document.getElementById("sentenceInput");
  const sentence = input.value.trim();
  if (!sentence) {
    showToast(t('sent_empty_warn'));
    return;
  }

  const resultEl = document.getElementById("analysisResult");
  const loadingEl = document.getElementById("analysisLoading");
  const btn = document.getElementById("analyzeBtn");

  loadingEl.style.display = "block";
  resultEl.innerHTML = "";
  btn.disabled = true;

  try {
    const data = await API.analyzeSentence(sentence);
    loadingEl.style.display = "none";
    btn.disabled = false;

    let html = `<div style="margin-top:16px">
      <div style="font-size:13px;font-weight:600;color:var(--text-secondary);margin-bottom:8px">${t('sent_token_title')}</div>
      <div class="token-row">`;

    for (const token of data.tokens || []) {
      const wi = token.word_info || {};
      const meaning = wi.chinese_meaning || wi.meaning_zh || wi.meaning_ja || wi.meaning_en || "";
      html += `
        <div class="token-capsule">
          <span class="token-original">${escapeHtml(token.original)}</span>
          ${meaning ? `<span class="token-meaning">${escapeHtml(meaning)}</span>` : ""}
          ${token.particles && token.particles.length ? `<span class="token-meaning">${token.particles.map(p=>escapeHtml(p.text)).join("+")}</span>` : ""}
        </div>`;
    }
    html += `</div></div>`;

    if (data.grammar_points && data.grammar_points.length) {
      html += `<div style="margin-top:20px">
        <div style="font-size:13px;font-weight:600;color:var(--text-secondary);margin-bottom:8px">${t('sent_grammar_title')}</div>`;

      for (const gp of data.grammar_points) {
        html += `
          <div class="grammar-card">
            <div class="grammar-pattern">${escapeHtml(gp.pattern)}</div>
            <div class="grammar-name">${escapeHtml(gp.explanation || "")}</div>
            ${gp.found_in ? `<div style="font-size:11px;color:var(--text-tertiary);margin-top:4px">${t('sent_grammar_found')}: ${escapeHtml(gp.found_in)}</div>` : ""}
          </div>`;
      }
      html += `</div>`;
    }

    if (data.translation_zh) {
      html += `
        <div class="translation-box">
          <div class="translation-label">${t('sent_translation')}</div>
          <div class="translation-text">${escapeHtml(data.translation_zh)}</div>
        </div>`;
    }

    resultEl.innerHTML = html;
  } catch (err) {
    loadingEl.style.display = "none";
    btn.disabled = false;
    resultEl.innerHTML = `<div class="empty-state" style="margin-top:20px"><h3>${t('sent_error')}</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}
