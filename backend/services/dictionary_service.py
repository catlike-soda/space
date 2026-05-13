"""Dictionary lookup service for SQLite database."""

from models.dictionary import db, Word, Conjugation, RelatedWord, ExampleSentence
from models.dictionary import GrammarPattern, Favorite


def search_words(query: str, lang: str = "kr", limit: int = 20) -> list:
    """Search words by Korean, Chinese, Japanese, or English.

    Args:
        query: Search term
        lang: 'kr', 'zh', 'ja', 'en'
        limit: Max results
    """
    q = query.strip()
    if not q:
        return []

    if lang == "zh":
        results = (Word.query
                   .filter(Word.chinese_meaning.contains(q))
                   .limit(limit)
                   .all())
    elif lang == "ja":
        results = (Word.query
                   .filter(Word.meaning_ja.contains(q))
                   .limit(limit)
                   .all())
    else:
        # Search by hangul (exact match first, then prefix, then contains)
        exact = Word.query.filter(Word.hangul == q).all()
        prefix = (Word.query
                  .filter(Word.hangul.startswith(q))
                  .filter(Word.hangul != q)
                  .limit(limit)
                  .all())
        contains = (Word.query
                    .filter(Word.hangul.contains(q))
                    .filter(~Word.hangul.startswith(q))
                    .limit(limit)
                    .all())

        results = exact + prefix + contains
        results = results[:limit]

    # Also search by pronunciation
    if len(results) < limit:
        pron_results = (Word.query
                        .filter(Word.pronunciation.contains(q.lower()))
                        .limit(limit - len(results))
                        .all())
        for w in pron_results:
            if w not in results:
                results.append(w)

    # Add meaning_for_ui field based on lang
    result_dicts = []
    for w in results:
        d = w.to_dict()
        if lang == "ja":
            d["meaning_for_ui"] = d.get("meaning_ja") or d.get("chinese_meaning", "")
        else:
            d["meaning_for_ui"] = d.get("chinese_meaning", "")
        result_dicts.append(d)

    return result_dicts


def get_word_detail(word_id: int) -> dict or None:
    """Get full word detail with relations."""
    word = Word.query.get(word_id)
    if not word:
        return None

    data = word.to_dict()
    data["meaning_for_ui"] = data.get("chinese_meaning", "")

    # Related words
    related = (RelatedWord.query
               .filter(RelatedWord.word_id == word_id)
               .all())
    data["related_words"] = [r.to_dict() for r in related]

    # Example sentences
    sentences = (ExampleSentence.query
                 .filter(ExampleSentence.word_id == word_id)
                 .all())
    data["example_sentences"] = [s.to_dict() for s in sentences]

    # Conjugation summary (counts, not all forms)
    conj_count = (Conjugation.query
                  .filter(Conjugation.word_id == word_id)
                  .count())
    data["conjugation_count"] = conj_count

    return data


def get_conjugations(word_id: int, honorific: bool = False,
                     speech_level: str = None, mood: str = None,
                     tense: str = None) -> list:
    """Get conjugation forms for a word.

    If no speech_level/mood/tense specified, returns all forms.
    """
    q = Conjugation.query.filter(Conjugation.word_id == word_id)
    q = q.filter(Conjugation.honorific == honorific)

    if speech_level:
        q = q.filter(Conjugation.speech_level == speech_level)
    if mood:
        q = q.filter(Conjugation.mood == mood)
    if tense:
        q = q.filter(Conjugation.tense == tense)

    conjugations = q.all()
    return [c.to_dict() for c in conjugations]


def get_grammar_patterns(level: str = "all") -> list:
    """Get grammar patterns."""
    q = GrammarPattern.query
    if level != "all":
        q = q.filter(GrammarPattern.usage_level == level)
    patterns = q.all()
    return [p.to_dict() for p in patterns]


def find_grammar_pattern(pattern_name: str) -> dict or None:
    """Find a grammar pattern by name."""
    g = GrammarPattern.query.filter(GrammarPattern.pattern == pattern_name).first()
    return g.to_dict() if g else None


def get_favorites() -> list:
    """Get all favorites."""
    favs = Favorite.query.order_by(Favorite.added_at.desc()).all()
    return [f.to_dict() for f in favs]


def add_favorite(word_id: int) -> bool:
    """Add a word to favorites."""
    existing = Favorite.query.filter(Favorite.word_id == word_id).first()
    if existing:
        return True
    fav = Favorite(word_id=word_id)
    db.session.add(fav)
    db.session.commit()
    return True


def remove_favorite(word_id: int) -> bool:
    """Remove a word from favorites."""
    fav = Favorite.query.filter(Favorite.word_id == word_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return True
