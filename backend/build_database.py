"""Build SQLite database from seed data with pre-computed conjugations.

Usage: python build_database.py
"""

import json
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.dictionary import db, Word, Conjugation, RelatedWord
from models.dictionary import ExampleSentence, GrammarPattern
from services.conjugation_engine import ConjugationEngine
from services.romanization import romanize
from services.irregular_handler import detect_irregular_type, extract_stem

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "seed_data")
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "korean_dict.db")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_database():
    # Skip if DB already exists and has data
    if os.path.exists(DB_PATH):
        # Quick check: if the DB file has reasonable size, skip rebuild
        if os.path.getsize(DB_PATH) > 10000:
            print(f"Database already exists: {DB_PATH}")
            print("Skipping rebuild. Delete the file manually to force rebuild.")
            return

    app = create_app()
    with app.app_context():
        db.create_all()
        print("Tables created.")

        # --- Import words ---
        words_data = load_json("topik_words.json")
        word_map = {}  # hangul → Word object

        for wd in words_data:
            hangul = wd["hangul"]
            stem = wd.get("stem") or extract_stem(hangul)
            irr_type = wd.get("irregular_type")
            if irr_type is None:
                detected = detect_irregular_type(hangul, stem)
                if detected:
                    irr_type = detected

            word = Word(
                hangul=hangul,
                pronunciation=romanize(hangul),
                type=wd["type"],
                chinese_meaning=wd.get("chinese_meaning", ""),
                meaning_ja=wd.get("meaning_ja", ""),
                definition_kr=wd.get("definition_kr", ""),
                level=wd.get("level", "beginner"),
                is_irregular=(irr_type is not None),
                irregular_type=irr_type,
                stem=stem,
            )
            db.session.add(word)
            word_map[hangul] = word

        db.session.commit()
        print(f"Imported {len(words_data)} words.")

        # --- Generate conjugations ---
        conj_count = 0
        for word in Word.query.all():
            if word.type not in ("verb", "adjective"):
                continue
            engine = ConjugationEngine(word.hangul, word.type,
                                       word.irregular_type, word.stem)
            forms = engine.generate_all(honorific=False)
            for f in forms:
                c = Conjugation(
                    word_id=word.id,
                    speech_level=f["speech_level"],
                    mood=f["mood"],
                    tense=f["tense"],
                    honorific=f["honorific"],
                    conjugated=f["conjugated"],
                    pronunciation=f["pronunciation"],
                )
                db.session.add(c)
                conj_count += 1

            # Also generate honorific forms
            forms_h = engine.generate_all(honorific=True)
            for f in forms_h:
                c = Conjugation(
                    word_id=word.id,
                    speech_level=f["speech_level"],
                    mood=f["mood"],
                    tense=f["tense"],
                    honorific=True,
                    conjugated=f["conjugated"],
                    pronunciation=f["pronunciation"],
                )
                db.session.add(c)
                conj_count += 1

        db.session.commit()
        print(f"Generated {conj_count} conjugation forms.")

        # --- Import grammar patterns ---
        grammar_data = load_json("grammar_patterns.json")
        for gp in grammar_data:
            g = GrammarPattern(
                pattern=gp["pattern"],
                name_zh=gp["name_zh"],
                description_zh=gp["description_zh"],
                usage_level=gp.get("usage_level", "all"),
                example_sentence=gp.get("example_sentence", ""),
                example_meaning=gp.get("example_meaning", ""),
            )
            db.session.add(g)
        db.session.commit()
        print(f"Imported {len(grammar_data)} grammar patterns.")

        # --- Import example sentences ---
        sent_data = load_json("example_sentences.json")
        sent_count = 0
        for entry in sent_data:
            hangul = entry["hangul"]
            word = Word.query.filter(Word.hangul == hangul).first()
            if not word:
                continue
            for s in entry["sentences"]:
                es = ExampleSentence(
                    word_id=word.id,
                    sentence_kr=s["kr"],
                    sentence_zh=s["zh"],
                    grammar_points=json.dumps(s.get("grammar", []),
                                              ensure_ascii=False),
                )
                db.session.add(es)
                sent_count += 1
        db.session.commit()
        print(f"Imported {sent_count} example sentences.")

        print(f"\nDatabase built successfully at: {DB_PATH}")
        print(f"Stats: {Word.query.count()} words, "
              f"{Conjugation.query.count()} conjugations, "
              f"{GrammarPattern.query.count()} grammar patterns")


if __name__ == "__main__":
    build_database()
