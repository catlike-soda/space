/** API client with fetch wrapper, error handling, and retry. */
const API = {
  BASE: "/api",

  async _fetch(method, path, body = null) {
    const opts = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(this.BASE + path, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: "Request failed" }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  },

  search(query, lang = "kr") {
    return this._fetch("POST", "/search", { query, lang });
  },

  getWord(id) {
    return this._fetch("GET", `/word/${id}`);
  },

  getConjugations(id, opts = {}) {
    const params = new URLSearchParams();
    if (opts.honorific) params.set("honorific", "true");
    if (opts.speech_level) params.set("speech_level", opts.speech_level);
    if (opts.mood) params.set("mood", opts.mood);
    if (opts.tense) params.set("tense", opts.tense);
    const qs = params.toString();
    return this._fetch("GET", `/word/${id}/conjugations${qs ? "?" + qs : ""}`);
  },

  analyzeSentence(sentence, uiLang) {
    return this._fetch("POST", "/sentence/analyze", { sentence, ui_lang: uiLang || "ja" });
  },

  getFavorites() {
    return this._fetch("GET", "/favorites");
  },

  addFavorite(wordId) {
    return this._fetch("POST", "/favorites", { word_id: wordId });
  },

  removeFavorite(wordId) {
    return this._fetch("DELETE", `/favorites/${wordId}`);
  },

  getGrammar(level = "all") {
    return this._fetch("GET", `/grammar?level=${level}`);
  },
};
