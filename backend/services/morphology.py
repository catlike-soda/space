"""Korean sentence morphological analysis.

Parses Korean sentences into tokens with:
- Particle stripping (이/가, 은/는, 을/를, 에, 에서, etc.)
- Verb/adjective ending analysis (reverse conjugation)
- Grammar point identification
"""

from .jamo_utils import decompose, compose, has_batchim, get_last_vowel
from .jamo_utils import CHOSUNG, JUNGSUNG, JONGSUNG

# Korean particles (조사) sorted by length (longest first)
PARTICLES = {
    "께서": "subject_honorific",
    "에서": "location_action",
    "으로": "direction_instrument",
    "에게": "dative",
    "한테": "dative_casual",
    "부터": "from",
    "까지": "until",
    "처럼": "like",
    "보다": "comparison",
    "조차": "even",
    "마저": "even",
    "이라고": "quotation_c",
    "라고": "quotation_v",
    "이나": "or_c",
    "나": "or_v",
    "이랑": "with_c",
    "랑": "with_v",
    "하고": "with",
    "에서": "from",
    "으로": "toward",
    "이": "subject_c",
    "가": "subject_v",
    "은": "topic_c",
    "는": "topic_v",
    "을": "object_c",
    "를": "object_v",
    "에": "location_time",
    "의": "possessive",
    "도": "also",
    "만": "only",
    "로": "direction_v",
}

# Verb endings (어미)
# Common final endings with their meaning
FINAL_ENDINGS = {
    "습니다": ("formal_polite", "declarative", "present"),
    "ㅂ니다": ("formal_polite", "declarative", "present"),
    "습니까": ("formal_polite", "interrogative", "present"),
    "ㅂ니까": ("formal_polite", "interrogative", "present"),
    "었습니다": ("formal_polite", "declarative", "past"),
    "았습니다": ("formal_polite", "declarative", "past"),
    "겠습니다": ("formal_polite", "declarative", "future"),
    "어요": ("informal_polite", "declarative", "present"),
    "아요": ("informal_polite", "declarative", "present"),
    "었어요": ("informal_polite", "declarative", "past"),
    "았어요": ("informal_polite", "declarative", "past"),
    "겠어요": ("informal_polite", "declarative", "future"),
    "어": ("informal_casual", "declarative", "present"),
    "아": ("informal_casual", "declarative", "present"),
    "었어": ("informal_casual", "declarative", "past"),
    "았어": ("informal_casual", "declarative", "past"),
    "겠어": ("informal_casual", "declarative", "future"),
    "으세요": ("informal_polite", "imperative", "present"),
    "세요": ("informal_polite", "imperative", "present"),
}

CONNECTIVE_ENDINGS = [
    "고", "며", "면", "서", "니까", "니", "지만", "는데", "ㄴ데",
    "러", "려고", "려면", "도록", "게", "지", "거나", "든지",
    "으려고", "으니까", "으면서", "으면", "은데",
]

# Modifier endings
MODIFIER_ENDINGS = ["는", "ㄴ", "은", "ㄹ", "을", "던"]

# Nominalizer endings
NOMINALIZER_ENDINGS = ["기", "ㅁ", "음"]


def tokenize(sentence: str) -> list:
    """Split Korean sentence by whitespace into eojeols."""
    return sentence.strip().split()


def strip_particles(eojeol: str) -> tuple:
    """Strip known particles from an eojeol.

    Returns (stem, [(particle_text, particle_type), ...])
    Example: '학교에는' → ('학교', [('에', 'location_time'), ('는', 'topic_v')])
    """
    stem = eojeol
    stripped = []

    # Try longest match first
    changed = True
    while changed:
        changed = False
        for particle, ptype in sorted(PARTICLES.items(), key=lambda x: -len(x[0])):
            if stem.endswith(particle) and len(stem) > len(particle):
                stem = stem[:-len(particle)]
                stripped.append((particle, ptype))
                changed = True
                break

    # Reverse to get original order
    stripped.reverse()
    return stem, stripped


def analyze_verb_ending(word: str) -> dict or None:
    """Try to identify verb/adjective ending and recover dictionary form.

    Returns dict with:
        possible_stem, ending_found, speech_level, mood, tense
    Or None if not identified.
    """
    if not word or len(word) < 2:
        return None

    # Try final endings first (longest match)
    for ending, (level, mood, tense) in sorted(FINAL_ENDINGS.items(),
                                                key=lambda x: -len(x[0])):
        if word.endswith(ending) and len(word) > len(ending):
            stem_candidate = word[:-len(ending)]
            return {
                "possible_stem": stem_candidate,
                "ending_found": ending,
                "speech_level": level,
                "mood": mood,
                "tense": tense,
            }

    # Try connective endings
    for ending in sorted(CONNECTIVE_ENDINGS, key=lambda x: -len(x)):
        if word.endswith(ending) and len(word) > len(ending):
            return {
                "possible_stem": word[:-len(ending)],
                "ending_found": ending,
                "speech_level": None,
                "mood": None,
                "tense": None,
                "connective": True,
            }

    # Try nominalizer
    for ending in NOMINALIZER_ENDINGS:
        if word.endswith(ending) and len(word) > len(ending):
            return {
                "possible_stem": word[:-len(ending)],
                "ending_found": ending,
                "speech_level": None,
                "mood": None,
                "tense": None,
                "nominalized": True,
            }

    return None


def analyze(sentence: str, dictionary_lookup_fn=None) -> dict:
    """Full sentence analysis pipeline.

    Args:
        sentence: Korean sentence to analyze
        dictionary_lookup_fn: Optional function to look up stems in dictionary.
                              Signature: fn(hangul: str) -> dict or None

    Returns:
        {
            "tokens": [...],
            "grammar_points": [...],
            "translation_zh": null (filled by LLM if needed)
        }
    """
    eojeols = tokenize(sentence)
    tokens = []
    grammar_points = []

    for eojeol in eojeols:
        token = {
            "original": eojeol,
            "stem": eojeol,
            "particles": [],
            "word_info": None,
            "conjugation": None,
        }

        # Step 1: Strip particles
        stem, particles = strip_particles(eojeol)
        token["stem"] = stem
        token["particles"] = [{"text": p[0], "type": p[1]} for p in particles]

        # Step 2: Look up stem in dictionary
        word_info = None
        if dictionary_lookup_fn:
            word_info = dictionary_lookup_fn(stem)
            if word_info:
                token["word_info"] = word_info

        # Step 3: If not found, try verb/adjective ending analysis
        if word_info is None:
            analysis = analyze_verb_ending(stem)
            if analysis:
                possible_stem = analysis["possible_stem"]
                token["conjugation"] = {
                    "ending_found": analysis["ending_found"],
                    "speech_level": analysis.get("speech_level"),
                    "mood": analysis.get("mood"),
                    "tense": analysis.get("tense"),
                    "connective": analysis.get("connective", False),
                    "nominalized": analysis.get("nominalized", False),
                }

                # Try to recover dictionary form
                if possible_stem and dictionary_lookup_fn:
                    word_info = dictionary_lookup_fn(possible_stem)
                    if word_info:
                        token["word_info"] = word_info

                # Try adding 다 to the stem
                if word_info is None and possible_stem and dictionary_lookup_fn:
                    dict_form = possible_stem + "다"
                    word_info = dictionary_lookup_fn(dict_form)
                    if word_info:
                        token["word_info"] = word_info

                # Add grammar point from the ending
                if analysis.get("ending_found"):
                    ending = analysis["ending_found"]
                    grammar_points.append({
                        "pattern": f"V/A-{ending}",
                        "explanation": _describe_ending(analysis),
                        "found_in": eojeol,
                    })

        # Add grammar points from particles
        for p in particles:
            ptext, ptype = p
            grammar_points.append({
                "pattern": f"N-{ptext}",
                "explanation": _describe_particle(ptype),
                "found_in": eojeol,
            })

        tokens.append(token)

    return {
        "tokens": tokens,
        "grammar_points": grammar_points,
        "translation_zh": None,
    }


def _describe_ending(analysis: dict) -> str:
    """Provide Chinese description of a verb ending."""
    if analysis.get("connective"):
        return f"连接词尾 -{analysis['ending_found']}"
    if analysis.get("nominalized"):
        return f"名词化词尾 -{analysis['ending_found']}"

    level = analysis.get("speech_level", "")
    mood = analysis.get("mood", "")
    tense = analysis.get("tense", "")

    level_names = {
        "formal_polite": "正式敬语(합쇼체)",
        "informal_polite": "非正式敬语(해요체)",
        "informal_casual": "半语(해체)",
        "formal_neutral": "半正式(하오체)",
    }
    mood_names = {
        "declarative": "陈述",
        "interrogative": "疑问",
        "imperative": "命令",
        "propositive": "共动",
    }
    tense_names = {
        "present": "现在时",
        "past": "过去时",
        "future": "将来时",
    }

    parts = []
    if tense in tense_names:
        parts.append(tense_names[tense])
    if mood in mood_names:
        parts.append(mood_names[mood])
    if level in level_names:
        parts.append(level_names[level])

    return " ".join(parts)


def _describe_particle(ptype: str) -> str:
    """Provide Chinese description of a particle."""
    desc = {
        "subject_honorific": "主语（尊称）",
        "subject_c": "主语（有终声）",
        "subject_v": "主语（无终声）",
        "topic_c": "主题/对比（有终声）",
        "topic_v": "主题/对比（无终声）",
        "object_c": "宾语（有终声）",
        "object_v": "宾语（无终声）",
        "location_time": "地点/时间",
        "location_action": "动作发生地点",
        "direction_instrument": "方向/工具",
        "direction_v": "方向（无终声）",
        "dative": "给予对象",
        "dative_casual": "给予对象（口语）",
        "from": "从...",
        "until": "到...为止",
        "like": "像...一样",
        "comparison": "比...",
        "even": "甚至...",
        "quotation_c": "引用（有终声）",
        "quotation_v": "引用（无终声）",
        "or_c": "或者（有终声）",
        "or_v": "或者（无终声）",
        "with_c": "和...（有终声）",
        "with_v": "和...（无终声）",
        "with": "和...",
        "possessive": "的/所属",
        "also": "也/还",
        "only": "只/仅",
    }
    return desc.get(ptype, f"助词({ptype})")
