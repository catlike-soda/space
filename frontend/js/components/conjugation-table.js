/** Conjugation table renderer. */

const ConjugationTable = {
  _levels: [
    { id: "informal_polite", kr: "해요체", key: "conj_informal_polite" },
    { id: "formal_polite", kr: "합쇼체", key: "conj_formal_polite" },
    { id: "informal_casual", kr: "해체", key: "conj_informal_casual" },
    { id: "formal_neutral", kr: "하오체", key: "conj_formal_neutral" },
  ],
  _moods: [
    { id: "declarative", key: "conj_declarative" },
    { id: "interrogative", key: "conj_interrogative" },
    { id: "imperative", key: "conj_imperative" },
    { id: "propositive", key: "conj_propositive" },
  ],
  _tenses: ["present", "past", "future"],
  _tenseKeys: { present: "conj_present", past: "conj_past", future: "conj_future" },

  render(conjugations, wordType, isIrregular) {
    if (!conjugations || !conjugations.length) {
      return `<div class="empty-state"><p>${t('conj_empty')}</p></div>`;
    }

    const lookup = {};
    for (const c of conjugations) {
      if (!lookup[c.speech_level]) lookup[c.speech_level] = {};
      if (!lookup[c.speech_level][c.mood]) lookup[c.speech_level][c.mood] = {};
      lookup[c.speech_level][c.mood][c.tense] = c;
    }

    const moods = wordType === "adjective"
      ? this._moods.filter(m => m.id === "declarative" || m.id === "interrogative")
      : this._moods;

    let html = `<div style="overflow-x:auto;-webkit-overflow-scrolling:touch">`;

    for (const level of this._levels) {
      if (!lookup[level.id]) continue;

      html += `<div style="margin-bottom:20px">`;
      html += `<div style="font-size:14px;font-weight:600;color:var(--accent);margin-bottom:8px">
                 ${t(level.key)} <span style="font-weight:400;font-size:12px;color:var(--text-secondary)">${level.kr}</span>
               </div>`;

      html += `<table class="conj-table" style="min-width:100%">
        <thead>
          <tr>
            <th style="width:50px">${t('conj_col_mood')}</th>
            ${this._tenses.map(tn => `<th>${t(this._tenseKeys[tn])}</th>`).join("")}
          </tr>
        </thead>
        <tbody>`;

      for (const mood of moods) {
        html += `<tr>
          <td>${t(mood.key)}</td>`;
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
                ⚠ ${t('conj_irregular_warn')}
              </div>`;
    }

    return html;
  },
};
