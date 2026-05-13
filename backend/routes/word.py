"""GET /api/word/<id> - Word detail and conjugations."""

from flask import Blueprint, request, jsonify
from services.dictionary_service import get_word_detail, get_conjugations
from services.conjugation_engine import ConjugationEngine
from models.dictionary import Word, Conjugation, db

word_bp = Blueprint("word", __name__)


@word_bp.route("/word/<int:word_id>", methods=["GET"])
def word_detail(word_id):
    word = get_word_detail(word_id)
    if not word:
        return jsonify({"error": "word not found"}), 404
    return jsonify(word)


@word_bp.route("/word/<int:word_id>/conjugations", methods=["GET"])
def word_conjugations(word_id):
    """Get conjugation forms. Supports query params:
        honorific=true/false
        speech_level=informal_polite (optional filter)
        mood=declarative (optional filter)
        tense=present (optional filter)
    """
    word = Word.query.get(word_id)
    if not word:
        return jsonify({"error": "word not found"}), 404

    honorific = request.args.get("honorific", "false").lower() == "true"
    speech_level = request.args.get("speech_level")
    mood = request.args.get("mood")
    tense = request.args.get("tense")

    # Only generate conjugations for verbs and adjectives
    if word.type not in ("verb", "adjective"):
        return jsonify({"conjugations": [], "word_type": word.type,
                        "message": "Conjugations only available for verbs and adjectives"})

    # Check if we have pre-computed conjugations
    existing = get_conjugations(word_id, honorific, speech_level, mood, tense)
    if existing:
        return jsonify({
            "word_id": word_id,
            "hangul": word.hangul,
            "type": word.type,
            "is_irregular": word.is_irregular,
            "irregular_type": word.irregular_type,
            "conjugations": existing,
            "source": "precomputed",
        })

    # Generate on-the-fly
    engine = ConjugationEngine(word.hangul, word.type, word.irregular_type,
                               word.stem)
    all_forms = engine.generate_all(honorific=honorific)

    # Apply optional filters
    if speech_level:
        all_forms = [f for f in all_forms if f["speech_level"] == speech_level]
    if mood:
        all_forms = [f for f in all_forms if f["mood"] == mood]
    if tense:
        all_forms = [f for f in all_forms if f["tense"] == tense]

    return jsonify({
        "word_id": word_id,
        "hangul": word.hangul,
        "type": word.type,
        "is_irregular": word.is_irregular,
        "irregular_type": word.irregular_type,
        "conjugations": all_forms,
        "source": "generated",
    })


@word_bp.route("/grammar", methods=["GET"])
def grammar_list():
    """Get grammar patterns."""
    from services.dictionary_service import get_grammar_patterns
    level = request.args.get("level", "all")
    patterns = get_grammar_patterns(level)
    return jsonify({"patterns": patterns})
