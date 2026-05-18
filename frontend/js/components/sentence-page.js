/** Sentence analysis page. */

function getParticleDesc(type) {
  const map = {
    subject_honorific: '主语(尊称)', subject_c: '主语', subject_v: '主语',
    topic_c: '主题', topic_v: '主题', object_c: '宾语', object_v: '宾语',
    location_time: '地点/时间', location_action: '动作地点',
    direction_instrument: '方向/工具', direction_v: '方向',
    dative: '给', dative_casual: '给(口语)', from: '从', until: '到',
    like: '像', comparison: '比', even: '甚至',
    quotation_c: '引用', quotation_v: '引用',
    or_c: '或', or_v: '或', with_c: '和', with_v: '和', with: '和',
    possessive: '的', also: '也', only: '只',
  };
  return map[type] || type;
}

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
    const data = await API.analyzeSentence(sentence, getLocale());
    loadingEl.style.display = "none";
    btn.disabled = false;

    let html = "";

    // 1. TRANSLATION ON TOP
    if (data.translation_zh) {
      html += `
        <div class="translation-box">
          <div class="translation-label">${t('sent_translation')}</div>
          <div class="translation-text">${escapeHtml(data.translation_zh)}</div>
        </div>`;
    }

    // 2. TOKEN BREAKDOWN — each word with meaning + grammar
    html += `<div class="token-row">`;

    for (const token of data.tokens || []) {
      const wi = token.word_info || {};
      const meaning = wi.chinese_meaning || wi.meaning_zh || wi.meaning_ja || wi.meaning_en || "";
      const grammarAI = wi.grammar_ai || "";
      const particles = token.particles || [];
      const conj = token.conjugation;

      html += `<div class="token-capsule">`;
      // Original + meaning (main line)
      html += `<div class="token-main">`;
      html += `<span class="token-original">${escapeHtml(token.original)}</span>`;
      html += `<span class="token-arrow">→</span>`;
      html += `<span class="token-meaning">${escapeHtml(meaning)}</span>`;
      html += `</div>`;

      // Grammar info line (compact)
      const grammarParts = [];

      // Particle info
      for (const p of particles) {
        const pDesc = getParticleDesc(p.type);
        grammarParts.push(`<span class="token-particle">${escapeHtml(p.text)}(${escapeHtml(pDesc)})</span>`);
      }

      // Verb ending info (local)
      if (conj && conj.ending_found) {
        const parts = [];
        if (conj.tense) parts.push(conj.tense === 'present' ? '现在' : conj.tense === 'past' ? '过去' : '将来');
        if (conj.mood) parts.push(conj.mood === 'declarative' ? '陈述' : conj.mood === 'interrogative' ? '疑问' : conj.mood === 'imperative' ? '命令' : '共动');
        if (conj.connective) parts.push('连接');
        if (conj.nominalized) parts.push('名词化');
        if (parts.length) grammarParts.push(`<span class="token-ending">${parts.join('·')}(${escapeHtml(conj.ending_found)})</span>`);
      }

      // AI grammar annotation
      if (grammarAI) {
        grammarParts.push(`<span class="token-grammar">${escapeHtml(grammarAI)}</span>`);
      }

      if (grammarParts.length) {
        html += `<div class="token-grammar-line">${grammarParts.join(' ')}</div>`;
      }

      html += `</div>`;
    }
    html += `</div>`;

    // 3. LOCAL GRAMMAR POINTS — compact
    const localGP = (data.grammar_points || []).filter(gp => !gp.explanation || (!gp.explanation.includes('≈') && !gp.explanation.includes('相当于') && !gp.explanation.includes('対応')));
    if (localGP.length) {
      html += `<div class="grammar-compact">`;
      html += `<div class="grammar-compact-title">${t('sent_grammar_title')}</div>`;
      for (const gp of localGP) {
        html += `<span class="grammar-tag">${escapeHtml(gp.pattern)} <small>${escapeHtml(gp.explanation)}</small></span>`;
      }
      html += `</div>`;
    }

    resultEl.innerHTML = html;
  } catch (err) {
    loadingEl.style.display = "none";
    btn.disabled = false;
    resultEl.innerHTML = `<div class="empty-state" style="margin-top:20px"><h3>${t('sent_error')}</h3><p>${escapeHtml(err.message)}</p></div>`;
  }
}
