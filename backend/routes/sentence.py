"""POST /api/sentence/analyze - Sentence grammar analysis with Gemini Flash."""

from flask import Blueprint, request, jsonify
from services.morphology import analyze
from services.llm_fallback import analyze_sentence as llm_analyze

sentence_bp = Blueprint("sentence", __name__)


@sentence_bp.route("/sentence/analyze", methods=["POST"])
def analyze_sentence():
    data = request.get_json(silent=True) or {}
    sentence = data.get("sentence", "").strip()
    ui_lang = data.get("ui_lang", "ja")

    if not sentence:
        return jsonify({"error": "sentence is required"}), 400

    if len(sentence) > 500:
        return jsonify({"error": "sentence too long (max 500 chars)"}), 400

    # Step 1: Local morphological analysis (particle stripping, ending detection)
    from models.dictionary import Word

    def dict_lookup(stem: str) -> dict or None:
        w = Word.query.filter(Word.hangul == stem).first()
        if w: return w.to_dict()
        w = Word.query.filter(Word.stem == stem).first()
        if w: return w.to_dict()
        w = Word.query.filter(Word.hangul == stem + "다").first()
        if w: return w.to_dict()
        return None

    result = analyze(sentence, dict_lookup)

    # Step 2: Always call Gemini Flash for high-quality analysis (free forever)
    llm_result = llm_analyze(sentence, ui_lang)
    if llm_result:
        if llm_result.get("translation"):
            result["translation_zh"] = llm_result["translation"]
        if llm_result.get("grammar_points"):
            for gp in llm_result.get("grammar_points", []):
                result["grammar_points"].append({
                    "pattern": gp.get("pattern", ""),
                    "explanation": gp.get("explanation", ""),
                })
        if llm_result.get("tokens"):
            for i, token in enumerate(result["tokens"]):
                if i < len(llm_result["tokens"]):
                    lt = llm_result["tokens"][i]
                    if token.get("word_info") is None:
                        token["word_info"] = {
                            "meaning_zh": lt.get("meaning", ""),
                            "grammar_role": lt.get("grammar_role", ""),
                            "dictionary_form": lt.get("dictionary_form"),
                        }

    return jsonify(result)
