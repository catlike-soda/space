"""Favorites API routes."""

from flask import Blueprint, request, jsonify
from services.dictionary_service import get_favorites, add_favorite, remove_favorite

favorites_bp = Blueprint("favorites", __name__)


@favorites_bp.route("/favorites", methods=["GET"])
def list_favorites():
    favs = get_favorites()
    return jsonify({"favorites": favs})


@favorites_bp.route("/favorites", methods=["POST"])
def add_favorite_route():
    data = request.get_json(silent=True) or {}
    word_id = data.get("word_id")
    if not word_id:
        return jsonify({"error": "word_id is required"}), 400
    add_favorite(int(word_id))
    return jsonify({"ok": True})


@favorites_bp.route("/favorites/<int:word_id>", methods=["DELETE"])
def remove_favorite_route(word_id):
    remove_favorite(word_id)
    return jsonify({"ok": True})
