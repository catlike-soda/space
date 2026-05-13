from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Word(db.Model):
    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key=True)
    hangul = db.Column(db.String(100), nullable=False, index=True)
    hanja = db.Column(db.String(100), nullable=True)
    pronunciation = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # noun, verb, adjective, adverb, determiner, etc.
    chinese_meaning = db.Column(db.String(500), nullable=False, default="")
    meaning_ja = db.Column(db.String(500), nullable=True)
    definition_kr = db.Column(db.String(1000), nullable=True)
    definition_en = db.Column(db.String(1000), nullable=True)
    level = db.Column(db.String(10), nullable=True)  # beginner, intermediate, advanced
    frequency = db.Column(db.Integer, default=0)
    is_irregular = db.Column(db.Boolean, default=False)
    irregular_type = db.Column(db.String(10), nullable=True)  # ㅂ, ㄷ, ㅅ, 르, ㄹ, ㅎ, 으
    stem = db.Column(db.String(100), nullable=True)

    conjugations = db.relationship("Conjugation", backref="word", lazy="dynamic",
                                   cascade="all, delete-orphan")
    sentences = db.relationship("ExampleSentence", backref="word", lazy="dynamic",
                                cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "hangul": self.hangul,
            "hanja": self.hanja,
            "pronunciation": self.pronunciation,
            "type": self.type,
            "chinese_meaning": self.chinese_meaning or "",
            "meaning_ja": self.meaning_ja or "",
            "definition_kr": self.definition_kr,
            "definition_en": self.definition_en,
            "level": self.level,
            "frequency": self.frequency,
            "is_irregular": self.is_irregular,
            "irregular_type": self.irregular_type,
            "stem": self.stem,
        }


class Conjugation(db.Model):
    __tablename__ = "conjugations"

    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=False, index=True)
    speech_level = db.Column(db.String(20), nullable=False)  # formal_polite, informal_polite, informal_casual, formal_neutral
    mood = db.Column(db.String(20), nullable=False)  # declarative, interrogative, imperative, propositive
    tense = db.Column(db.String(20), nullable=False)  # present, past, future
    honorific = db.Column(db.Boolean, default=False)
    conjugated = db.Column(db.String(200), nullable=False)
    pronunciation = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "speech_level": self.speech_level,
            "mood": self.mood,
            "tense": self.tense,
            "honorific": self.honorific,
            "conjugated": self.conjugated,
            "pronunciation": self.pronunciation,
        }


class RelatedWord(db.Model):
    __tablename__ = "related_words"

    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=False, index=True)
    related_id = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=False)
    relation_type = db.Column(db.String(20), nullable=False)  # synonym, antonym, derived, compound

    word = db.relationship("Word", foreign_keys=[word_id])
    related = db.relationship("Word", foreign_keys=[related_id])

    def to_dict(self):
        return {
            "relation_type": self.relation_type,
            "word": self.related.to_dict() if self.related else None,
        }


class ExampleSentence(db.Model):
    __tablename__ = "example_sentences"

    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=False, index=True)
    sentence_kr = db.Column(db.String(1000), nullable=False)
    sentence_zh = db.Column(db.String(1000), nullable=False)
    grammar_points = db.Column(db.String(500), nullable=True)  # JSON array of pattern IDs

    def to_dict(self):
        return {
            "id": self.id,
            "sentence_kr": self.sentence_kr,
            "sentence_zh": self.sentence_zh,
            "grammar_points": self.grammar_points,
        }


class GrammarPattern(db.Model):
    __tablename__ = "grammar_patterns"

    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(100), nullable=False)
    name_zh = db.Column(db.String(200), nullable=False)
    description_zh = db.Column(db.Text, nullable=False)
    usage_level = db.Column(db.String(20), nullable=True)
    example_sentence = db.Column(db.String(500), nullable=True)
    example_meaning = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "pattern": self.pattern,
            "name_zh": self.name_zh,
            "description_zh": self.description_zh,
            "usage_level": self.usage_level,
            "example_sentence": self.example_sentence,
            "example_meaning": self.example_meaning,
        }


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=False, unique=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    word = db.relationship("Word", backref="favorite")

    def to_dict(self):
        return {
            "id": self.id,
            "word_id": self.word_id,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "word": self.word.to_dict() if self.word else None,
        }
