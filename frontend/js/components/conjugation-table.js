/** Conjugation table renderer. */

const ConjugationTable = {
  _levels: [
    { id: "informal_polite", kr: "해요체", zh: "非正式敬语" },
    { id: "formal_polite", kr: "합쇼체", zh: "正式敬语" },
    { id: "informal_casual", kr: "해체", zh: "半语" },
    { id: "formal_neutral", kr: "하오체", zh: "半正式语" },
  ],
  _moods: [
    { id: "declarative", zh: "陈述" },
    { id: "interrogative", zh: "疑问" },
    { id: "imperative", zh: "命令" },
    { id: "propositive", zh: "共动" },
  ],
  _tenses: ["present", "past", "future"],
  _tenseLabels: { present: "现在", past: "过去", future: "将来" },

  render(conjugations, wordType, isIrregular) {
    if (!conjugations || !conjugations.length) {
      return '<div class="empty-state"><p>暂无用形数据</p></div>';
    }

    // Build lookup: level -> mood -> tense -> form
    const lookup = {};
    for (const c of conjugations) {
      if (!lookup[c.speech_level]) lookup[c.speech_level] = {};
      if (!lookup[c.speech_level][c.mood]) lookup[c.speech_level][c.mood] = {};
      lookup[c.speech_level][c.mood][c.tense] = c;
    }

    // Filter applicable moods by word type
    const moods = wordType === "adjective"
      ? this._moods.filter(m => m.id === "declarative" || m.id === "interrogative")
      : this._moods;

    let html = `<div style="overflow-x:auto;-webkit-overflow-scrolling:touch">`;

    for (const level of this._levels) {
      if (!lookup[level.id]) continue;

      html += `<div style="margin-bottom:20px">`;
      html += `<div style="font-size:14px;font-weight:600;color:var(--accent);margin-bottom:8px">
                 ${level.zh} <span style="font-weight:400;font-size:12px;color:var(--text-secondary)">${level.kr}</span>
               </div>`;

      // Desktop table
      html += `<table class="conj-table" style="min-width:100%">
        <thead>
          <tr>
            <th style="width:50px">语气</th>
            ${this._tenses.map(t => `<th>${this._tenseLabels[t]}</th>`).join("")}
          </tr>
        </thead>
        <tbody>`;

      for (const mood of moods) {
        html += `<tr>
          <td>${mood.zh}</td>`;
        for (const tense of this._tenses) {
          const form = lookup[level.id][mood.id]?.[tense];
          if (form) {
            html += `<td>
              <span class="conj-form">${escapeHtml(form.conjugated)}</span>
              <span class="conj-pron">[${escapeHtml(form.pronunciation)}]</span>
            </td>`;
          } else {
            html += `<td><span style="color:var(--text-tertiary)">-</span></td>`;
          }
        }
        html += `</tr>`;
      }

      html += `</tbody></table></div>`;
    }

    html += `</div>`;

    if (isIrregular) {
      html += `<div style="margin-top:12px;padding:10px 14px;background:#FFF3CD;border-radius:8px;font-size:12px;color:#856404">
                ⚠ 此单词为不规则词，部分变形形式需特别记忆
              </div>`;
    }

    return html;
  },
};
