"""Korean speech level definitions.

4 speech levels x 4 moods x 3 tenses = 48 base forms.
Ending patterns use these markers:
  - {B} = adds ㅂ/습 depending on batchim
  - {N} = adds 는/ㄴ depending on batchim
  - {A} = adds 아/어 depending on vowel harmony (yang=아, yin=어)
  - {SS} = adds 았/었 depending on vowel harmony
  - {LK} = adds ㄹ/을 depending on batchim
  - {E} = empty string (removed)
"""

# Each entry: (has_batchim_form, no_batchim_form)
# The form patterns are resolved at conjugation time.

SPEECH_LEVELS = {
    "formal_polite": {
        "name_kr": "하십시오체",
        "name_zh": "正式敬语 (합쇼체)",
        "declarative": {
            "present": ("습니다", "ㅂ니다"),
            "past": ("었습니다", "았습니다"),
            "future": ("겠습니다", "겠습니다"),
        },
        "interrogative": {
            "present": ("습니까", "ㅂ니까"),
            "past": ("었습니까", "았습니까"),
            "future": ("겠습니까", "겠습니까"),
        },
        "imperative": {
            "present": ("으십시오", "십시오"),
            "past": ("으셨습니다", "셨습니다"),
            # imperative past is rarely used, using honorific declarative past
        },
        "propositive": {
            "present": ("읍시다", "ㅂ시다"),
            "past": ("었읍시다", "았읍시다"),
            # propositive past is rare
        },
    },
    "informal_polite": {
        "name_kr": "해요체",
        "name_zh": "非正式敬语 (해요체)",
        "declarative": {
            "present": ("어요", "아요"),
            "past": ("었어요", "았어요"),
            "future": ("겠어요", "겠어요"),
        },
        "interrogative": {
            "present": ("어요", "아요"),
            "past": ("었어요", "았어요"),
            "future": ("겠어요", "겠어요"),
        },
        "imperative": {
            "present": ("으세요", "세요"),
            "past": ("으셨어요", "셨어요"),
        },
        "propositive": {
            "present": ("어요", "아요"),
            "past": ("었어요", "았어요"),
        },
    },
    "informal_casual": {
        "name_kr": "해체",
        "name_zh": "半语 (반말)",
        "declarative": {
            "present": ("어", "아"),
            "past": ("었어", "았어"),
            "future": ("겠어", "겠어"),
        },
        "interrogative": {
            "present": ("어", "아"),
            "past": ("었어", "았어"),
            "future": ("겠어", "겠어"),
        },
        "imperative": {
            "present": ("어", "아"),
            "past": ("었어", "았어"),
        },
        "propositive": {
            "present": ("어", "아"),
            "past": ("었어", "았어"),
        },
    },
    "formal_neutral": {
        "name_kr": "하오체",
        "name_zh": "半正式语 (하오체)",
        "declarative": {
            "present": ("소", "오"),
            "past": ("었소", "았소"),
            "future": ("겠소", "겠소"),
        },
        "interrogative": {
            "present": ("소", "오"),
            "past": ("었소", "았소"),
            "future": ("겠소", "겠소"),
        },
        "imperative": {
            "present": ("시오", "오"),
            "past": ("셨소", "셨소"),
        },
        "propositive": {
            "present": ("읍시다", "ㅂ시다"),
            "past": ("었읍시다", "았읍시다"),
        },
    },
}

MOODS = ["declarative", "interrogative", "imperative", "propositive"]
TENSES = ["present", "past", "future"]

# Vowel harmony groups
YANG_VOWELS = {"ㅏ", "ㅗ", "ㅑ", "ㅛ", "ㅘ", "ㅚ", "ㅐ"}
YIN_VOWELS = {"ㅓ", "ㅜ", "ㅕ", "ㅠ", "ㅡ", "ㅢ", "ㅔ", "ㅝ", "ㅟ", "ㅖ", "ㅞ", "ㅙ"}

# Speech level display order (most common first)
LEVEL_ORDER = ["informal_polite", "formal_polite", "informal_casual", "formal_neutral"]
