"""Auto-generate example sentences & related words for vocabulary.
Usage: python build_examples.py
Outputs example_sentences.json and related_words.json
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.jamo_utils import has_batchim, get_last_vowel, decompose, JUNGSUNG

DATA_DIR = "data/seed_data"

# ── Sentence templates per word type ──
VERB_TEMPLATES = [
    ("저는 매일 {word}니다", "我每天{meaning}"),
    ("{word}고 싶어요", "想{meaning}"),
    ("어제 {word}었어요", "昨天{meaning}了"),
    ("지금 {word}고 있어요", "正在{meaning}"),
    ("내일 {word}을 거예요", "明天要{meaning}"),
    ("같이 {word}요", "一起{meaning}吧"),
]

ADJ_TEMPLATES = [
    ("정말 {word}니다", "真的很{meaning}"),
    ("너무 {word}어요", "太{meaning}了"),
    ("이것은 {word}니다", "这个很{meaning}"),
    ("요즘 {word}어요", "最近很{meaning}"),
    ("별로 {word}지 않아요", "不太{meaning}"),
]

NOUN_TEMPLATES = [
    ("이것은 {word}입니다", "这是{meaning}"),
    ("{word}을/를 좋아해요", "喜欢{meaning}"),
    ("{word}이/가 있어요", "有{meaning}"),
    ("{word}을/를 샀어요", "买了{meaning}"),
    ("{word}이/가 필요해요", "需要{meaning}"),
]

# ── Conjugation helper ──
def conj_present_polite(word, pos):
    """Generate 해요체 present form."""
    if pos == "noun" or pos in ("pronoun", "numeral", "determiner", "interjection"):
        return word
    from services.irregular_handler import extract_stem, detect_irregular_type, apply_irregular
    from services.speech_levels import YANG_VOWELS

    if word.endswith("다"):
        stem = extract_stem(word)
    else:
        stem = word

    if stem == "하":
        return "해요"

    irr = detect_irregular_type(word if word.endswith("다") else word + "다", stem)
    if pos == "adjective" and stem.endswith("있"):
        return stem + "어요"
    if pos == "adjective" and stem.endswith("없"):
        return stem + "어요"

    last_vowel = get_last_vowel(stem[-1]) if stem else ""
    if last_vowel in YANG_VOWELS:
        ending = "아요"
    else:
        ending = "어요"

    if irr:
        from services.irregular_handler import _handle_bieup, _handle_digeut, _handle_siot
        from services.irregular_handler import _handle_reu, _handle_rieul, _handle_hieut, _handle_eu
        if irr == "ㅂ":
            stem = _handle_bieup(stem)
        elif irr == "ㄷ":
            stem = _handle_digeut(stem)
        elif irr == "ㅅ":
            stem = _handle_siot(stem)
        elif irr == "르":
            stem = _handle_reu(stem)
        elif irr == "ㄹ":
            stem = _handle_rieul(stem, ending)
        elif irr == "ㅎ":
            stem = _handle_hieut(stem)
        elif irr == "으":
            stem = _handle_eu(stem, ending)

    if has_batchim(stem):
        return stem + ending
    else:
        # vowel merger
        last = stem[-1]
        cho, jung, jong = decompose(last)
        if jung >= 0:
            from jamo_utils import JUNGSUNG
            stem_vowel = JUNGSUNG[jung]
            end_first = ending[0]  # 아 or 어
            # Same vowel merges
            if stem_vowel == "ㅏ" and end_first == "아":
                # 가 + 아요 → 가요
                return stem + ending[1:]
            elif stem_vowel == "ㅓ" and end_first == "어":
                return stem + ending[1:]
            elif stem_vowel == "ㅗ" and end_first == "아":
                return stem + "와" + ending[2:] if len(ending) > 2 else stem + "와요"
            elif stem_vowel == "ㅜ" and end_first == "어":
                return stem + "워" + ending[2:] if len(ending) > 2 else stem + "워요"
            elif stem_vowel == "ㅡ" and end_first == "어":
                return stem[:-1] + "어" + ending[1:] if len(ending) > 1 else stem[:-1] + "어요"
        return stem + ending


def conj_past_polite(word, pos):
    """Generate 해요체 past form."""
    present = conj_present_polite(word, pos)
    if "해요" in present:
        return present.replace("해요", "했어요")
    if "어요" in present:
        return present.replace("어요", "었어요")
    if "아요" in present:
        return present.replace("아요", "았어요")
    return present


def conj_future_polite(word, pos):
    """Generate 해요체 future form."""
    if pos == "noun" or pos in ("pronoun", "numeral", "determiner", "interjection"):
        return word
    from services.irregular_handler import extract_stem as _extract_stem
    stem = _extract_stem(word) if word.endswith("다") else word
    if has_batchim(stem):
        return stem + "을 거예요"
    return stem + "ㄹ 거예요"


def conj_neg(word, pos):
    """Generate negative form."""
    if pos == "noun" or pos in ("pronoun", "numeral", "determiner", "interjection"):
        return word
    from services.irregular_handler import extract_stem
    stem = extract_stem(word) if word.endswith("다") else word
    return stem + "지 않아요"


def pick_particle(word, template_has_particle):
    """Pick correct particle based on batchim."""
    if "이/가" in template_has_particle:
        subj = template_has_particle
        if has_batchim(word[-1]):
            return subj.replace("이/가", "이")
        else:
            return subj.replace("이/가", "가")
    if "을/를" in template_has_particle:
        if has_batchim(word[-1]):
            return template_has_particle.replace("을/를", "을")
        else:
            return template_has_particle.replace("을/를", "를")
    return template_has_particle


def fill_template(word, pos, meaning, template_kr, template_zh):
    """Fill a sentence template with conjugated word."""
    from services.irregular_handler import extract_stem

    stem = extract_stem(word) if word.endswith("다") else word
    w = word  # full conjugated form
    if pos in ("verb", "adjective"):
        if "지 않" in template_kr:
            w = conj_neg(word, pos)
        elif "었" in template_kr or "았" in template_kr:
            w = conj_past_polite(word, pos)
        elif "을 거" in template_kr or "ㄹ 거" in template_kr:
            w = conj_future_polite(word, pos)
        elif "세요" in template_kr:
            if has_batchim(stem):
                w = stem + "으세요"
            else:
                w = stem + "세요"
        elif "고 싶" in template_kr or "고 있" in template_kr or "고 " in template_kr:
            # Template already has the grammar pattern; just use stem
            w = stem
        elif "{stem}" in template_kr:
            w = stem
        else:
            w = conj_present_polite(word, pos)

    if pos == "noun":
        kr = pick_particle(word, template_kr)
    else:
        kr = template_kr

    kr = kr.replace("{word}", w if pos in ("verb", "adjective") else word)
    kr = kr.replace("{stem}", stem if pos in ("verb", "adjective") else word)
    kr = kr.replace("{meaning}", meaning)
    zh = template_zh.replace("{meaning}", meaning)
    return kr, zh


# ── Related words: synonym/antonym mappings ──
SYNONYMS = {
    "가다": ["다니다", "걷다"],
    "오다": ["도착하다", "돌아오다"],
    "먹다": ["식사하다", "섭취하다"],
    "마시다": ["음용하다"],
    "보다": ["바라보다", "관찰하다", "쳐다보다"],
    "좋다": ["마음에 들다", "훌륭하다"],
    "나쁘다": ["좋지 않다", "안 좋다"],
    "크다": ["거대하다", "넓다"],
    "작다": ["좁다", "자그마하다"],
    "많다": ["풍부하다", "넘치다"],
    "적다": ["부족하다", "모자라다"],
    "예쁘다": ["아름답다", "곱다", "귀엽다"],
    "춥다": ["차갑다", "싸늘하다"],
    "덥다": ["뜨겁다", "무덥다"],
    "쉽다": ["간단하다", "용이하다"],
    "어렵다": ["힘들다", "까다롭다", "복잡하다"],
    "빠르다": ["신속하다", "급하다"],
    "느리다": ["천천하다", "더디다"],
    "기쁘다": ["행복하다", "즐겁다"],
    "슬프다": ["우울하다", "서글프다", "괴롭다"],
    "무섭다": ["두렵다", "공포스럽다"],
    "배우다": ["공부하다", "익히다"],
    "가르치다": ["교육하다", "지도하다"],
    "만들다": ["제작하다", "생산하다"],
    "웃다": ["미소짓다", "방긋하다"],
    "울다": ["눈물흘리다", "흐느끼다"],
    "사랑하다": ["좋아하다", "아끼다"],
    "미워하다": ["싫어하다", "증오하다"],
    "화내다": ["분노하다", "짜증내다"],
    "걱정하다": ["근심하다", "고민하다"],
    "이해하다": ["파악하다", "깨닫다"],
    "알다": ["인지하다", "파악하다"],
    "모르다": ["이해못하다", "무지하다"],
    "생각하다": ["고민하다", "사색하다"],
    "느끼다": ["감지하다", "인식하다"],
    "찾다": ["발견하다", "탐색하다"],
    "도와주다": ["돕다", "협력하다"],
    "기다리다": ["대기하다", "고대하다"],
    "사용하다": ["쓰다", "이용하다"],
    "이야기하다": ["말하다", "대화하다"],
    "시작하다": ["개시하다", "착수하다"],
    "끝내다": ["마치다", "종료하다"],
    "쉬다": ["휴식하다", "머무르다"],
    "일하다": ["근무하다", "노동하다"],
    "공부하다": ["학습하다", "배우다"],
    "감사하다": ["고마워하다", "감사드리다"],
    "바쁘다": ["여유없다", "분주하다"],
    "깨끗하다": ["청결하다", "맑다"],
    "더럽다": ["불결하다", "지저분하다"],
    "조용하다": ["고요하다", "정적하다"],
    "시끄럽다": ["소란하다", "떠들썩하다"],
}

ANTONYMS = {
    "가다": ["오다"],
    "오다": ["가다"],
    "크다": ["작다"],
    "작다": ["크다"],
    "많다": ["적다"],
    "적다": ["많다"],
    "좋다": ["나쁘다"],
    "나쁘다": ["좋다"],
    "쉽다": ["어렵다"],
    "어렵다": ["쉽다"],
    "빠르다": ["느리다"],
    "느리다": ["빠르다"],
    "춥다": ["덥다"],
    "덥다": ["춥다"],
    "기쁘다": ["슬프다"],
    "슬프다": ["기쁘다"],
    "가볍다": ["무겁다"],
    "무겁다": ["가볍다"],
    "길다": ["짧다"],
    "짧다": ["길다"],
    "높다": ["낮다"],
    "낮다": ["높다"],
    "넓다": ["좁다"],
    "좁다": ["넓다"],
    "비싸다": ["싸다"],
    "싸다": ["비싸다"],
    "깨끗하다": ["더럽다"],
    "더럽다": ["깨끗하다"],
    "조용하다": ["시끄럽다"],
    "시끄럽다": ["조용하다"],
    "웃다": ["울다"],
    "울다": ["웃다"],
    "사랑하다": ["미워하다"],
    "미워하다": ["사랑하다"],
    "알다": ["모르다"],
    "모르다": ["알다"],
    "열다": ["닫다"],
    "닫다": ["열다"],
    "사다": ["팔다"],
    "팔다": ["사다"],
    "입다": ["벗다"],
    "벗다": ["입다"],
    "주다": ["받다"],
    "받다": ["주다"],
    "시작하다": ["끝내다"],
    "끝내다": ["시작하다"],
    "일어나다": ["자다"],
    "자다": ["일어나다"],
    "강하다": ["약하다"],
    "약하다": ["강하다"],
    "뜨겁다": ["차갑다"],
    "차갑다": ["뜨겁다"],
    "바쁘다": ["한가하다"],
    "한가하다": ["바쁘다"],
    "맛있다": ["맛없다"],
    "맛없다": ["맛있다"],
    "재미있다": ["재미없다"],
    "재미없다": ["재미있다"],
    "안전하다": ["위험하다"],
    "위험하다": ["안전하다"],
    "건강하다": ["아프다"],
    "아프다": ["건강하다"],
    "편하다": ["불편하다"],
    "불편하다": ["편하다"],
    "착하다": ["나쁘다"],
    "성공하다": ["실패하다"],
    "실패하다": ["성공하다"],
    "자유": ["구속"],
    "평화": ["전쟁"],
    "행복": ["불행"],
    "희망": ["절망"],
    "사랑": ["증오"],
}


def build_sentences(words):
    """Generate example sentences for each word."""
    sent_map = {}  # hangul → [{kr, zh, grammar}]
    templates = {
        "verb": VERB_TEMPLATES,
        "adjective": ADJ_TEMPLATES,
        "noun": NOUN_TEMPLATES,
    }

    for w in words:
        hangul = w["hangul"]
        pos = w["type"]
        meaning = w.get("chinese_meaning", w.get("meaning_ja", ""))
        if pos not in templates:
            pos = "noun"

        tmpls = templates.get(pos, NOUN_TEMPLATES)
        # Generate 2-3 valid sentences
        sents = []
        for t_kr, t_zh in tmpls[:3]:  # First 3 templates per word
            try:
                kr, zh = fill_template(hangul, pos, meaning, t_kr, t_zh)
                # Clean up the meaning in the template
                kr = kr.replace("{meaning}", meaning)
                zh = zh.replace("{meaning}", meaning)
                sents.append({"kr": kr, "zh": zh, "grammar": []})
            except Exception:
                continue
        if sents:
            sent_map[hangul] = sents

    return sent_map


def build_related(words):
    """Build related word pairs from synonym/antonym mappings."""
    # Build lookup
    word_lookup = {}
    for w in words:
        word_lookup[w["hangul"]] = w

    related = []
    seen = set()

    for w in words:
        hangul = w["hangul"]

        # Synonyms
        syns = SYNONYMS.get(hangul, [])
        for syn in syns:
            if syn in word_lookup and syn != hangul:
                key = tuple(sorted([hangul, syn, "synonym"]))
                if key not in seen:
                    related.append({"hangul": hangul, "related": syn, "type": "synonym"})
                    seen.add(key)

        # Antonyms
        ants = ANTONYMS.get(hangul, [])
        for ant in ants:
            if ant in word_lookup and ant != hangul:
                key = tuple(sorted([hangul, ant, "antonym"]))
                if key not in seen:
                    related.append({"hangul": hangul, "related": ant, "type": "antonym"})
                    seen.add(key)

    return related


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with open("data/seed_data/topik_words.json", "r", encoding="utf-8") as f:
        words = json.load(f)

    # Generate sentences
    sent_map = build_sentences(words)
    sent_output = []
    for hangul, sents in sent_map.items():
        sent_output.append({"hangul": hangul, "sentences": sents})

    with open("data/seed_data/example_sentences.json", "w", encoding="utf-8") as f:
        json.dump(sent_output, f, ensure_ascii=False, indent=2)

    # Generate related words
    related = build_related(words)
    with open("data/seed_data/related_words.json", "w", encoding="utf-8") as f:
        json.dump(related, f, ensure_ascii=False, indent=2)

    word_count = len(sent_output)
    sent_count = sum(len(s["sentences"]) for s in sent_output)
    related_count = len(related)
    sys.stderr.write(f"\nGenerated {sent_count} example sentences for {word_count} words\n")
    sys.stderr.write(f"Generated {related_count} related word pairs\n")
