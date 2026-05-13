"""POST /api/search - Search word by Korean or Chinese."""

from flask import Blueprint, request, jsonify
from services.dictionary_service import search_words

search_bp = Blueprint("search", __name__)


@search_bp.route("/search", methods=["POST"])
def search():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    lang = data.get("lang", "kr")

    if not query:
        return jsonify({"results": [], "query": ""})

    if lang not in ("kr", "zh", "ja", "kr_ja"):
        lang = "kr"

    results = search_words(query, lang)
    return jsonify({"results": results, "query": query, "lang": lang})
