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

    # Step 2: AI enrichment via DeepSeek
    llm_result = llm_analyze(sentence, ui_lang)
    if llm_result:
        if llm_result.get("translation"):
            result["translation_zh"] = llm_result["translation"]
        if llm_result.get("tokens"):
            llm_token_map = {}
            for lt in llm_result["tokens"]:
                key = lt.get("original", "").strip()
                if key:
                    llm_token_map[key] = lt

            for token in result["tokens"]:
                orig = token.get("original", "")
                lt = llm_token_map.get(orig)
                if lt is None:
                    for key, val in llm_token_map.items():
                        if key in orig or orig in key:
                            lt = val
                            break
                if lt:
                    ai_meaning = lt.get("meaning", "")
                    ai_grammar = lt.get("grammar", "")
                    if token.get("word_info") is None:
                        token["word_info"] = {
                            "meaning_zh": ai_meaning,
                            "grammar_ai": ai_grammar,
                        }
                    else:
                        token["word_info"]["grammar_ai"] = ai_grammar
                        if not token["word_info"].get("meaning_zh"):
                            token["word_info"]["meaning_zh"] = ai_meaning

    return jsonify(result)
