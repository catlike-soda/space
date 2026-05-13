"""POST /api/sentence/analyze - Sentence grammar analysis."""

from flask import Blueprint, request, jsonify
from services.morphology import analyze
from services.llm_fallback import analyze_sentence as llm_analyze

sentence_bp = Blueprint("sentence", __name__)


@sentence_bp.route("/sentence/analyze", methods=["POST"])
def analyze_sentence():
    data = request.get_json(silent=True) or {}
    sentence = data.get("sentence", "").strip()

    if not sentence:
        return jsonify({"error": "sentence is required"}), 400

    if len(sentence) > 500:
        return jsonify({"error": "sentence too long (max 500 chars)"}), 400

    # Build a simple dictionary lookup function
    from models.dictionary import Word

    def dict_lookup(stem: str) -> dict or None:
        # Try exact match on hangul
        w = Word.query.filter(Word.hangul == stem).first()
        if w:
            return w.to_dict()
        # Try stem match
        w = Word.query.filter(Word.stem == stem).first()
        if w:
            return w.to_dict()
        # Try hangul ending with
        w = Word.query.filter(Word.hangul == stem + "다").first()
        if w:
            return w.to_dict()
        return None

    # First pass: local morphological analysis
    result = analyze(sentence, dict_lookup)

    # Second pass: if many tokens unresolved, try LLM
    unresolved = sum(1 for t in result["tokens"]
                     if t["word_info"] is None and not t["conjugation"])

    if unresolved > 0:
        llm_result = llm_analyze(sentence)
        if llm_result:
            # Merge LLM results
            if llm_result.get("translation_zh"):
                result["translation_zh"] = llm_result["translation_zh"]
            if llm_result.get("grammar_points"):
                existing = {g["pattern"] for g in result["grammar_points"]}
                for gp in llm_result.get("grammar_points", []):
                    if gp["pattern"] not in existing:
                        result["grammar_points"].append(gp)
                        existing.add(gp["pattern"])
            if llm_result.get("tokens"):
                # Use LLM tokens for unresolved ones
                for i, token in enumerate(result["tokens"]):
                    if (token["word_info"] is None
                            and not token["conjugation"]
                            and i < len(llm_result["tokens"])):
                        token["word_info"] = {
                            "meaning_zh": llm_result["tokens"][i].get("meaning_zh", ""),
                            "grammar_role": llm_result["tokens"][i].get("grammar_role", ""),
                            "dictionary_form": llm_result["tokens"][i].get("dictionary_form"),
                        }

    return jsonify(result)
