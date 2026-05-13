import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models.dictionary import db

_frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


def create_app():
    app = Flask(__name__, static_folder=_frontend_path, static_url_path="")
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    with app.app_context():
        from models.dictionary import Word, Conjugation, RelatedWord, ExampleSentence
        from models.dictionary import GrammarPattern, Favorite
        db.create_all()

    from routes.search import search_bp
    from routes.word import word_bp
    from routes.sentence import sentence_bp
    from routes.favorites import favorites_bp

    app.register_blueprint(search_bp, url_prefix="/api")
    app.register_blueprint(word_bp, url_prefix="/api")
    app.register_blueprint(sentence_bp, url_prefix="/api")
    app.register_blueprint(favorites_bp, url_prefix="/api")

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    @app.route("/")
    def serve_index():
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
