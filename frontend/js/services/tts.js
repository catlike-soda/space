/** Korean Text-to-Speech using Web Speech API. */
const TTS = {
  _synth: window.speechSynthesis,
  _voice: null,

  _getKoreanVoice() {
    if (this._voice) return this._voice;
    const voices = this._synth.getVoices();
    // Prefer native Korean voice
    this._voice = (
      voices.find(v => v.lang === "ko-KR" && v.localService) ||
      voices.find(v => v.lang === "ko-KR") ||
      voices.find(v => v.lang === "ko") ||
      null
    );
    return this._voice;
  },

  speak(text) {
    if (!this._synth) return;
    this._synth.cancel();

    const voice = this._getKoreanVoice();
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = "ko-KR";
    utt.rate = 0.85;
    utt.pitch = 1.0;
    if (voice) utt.voice = voice;
    this._synth.speak(utt);
  },

  stop() {
    if (this._synth) this._synth.cancel();
  },
};

// Ensure voices are loaded (Chrome loads them async)
if (window.speechSynthesis) {
  speechSynthesis.onvoiceschanged = () => { TTS._voice = null; };
  speechSynthesis.getVoices(); // trigger initial load
}
