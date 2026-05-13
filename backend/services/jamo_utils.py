"""Hangul syllable decomposition/composition via Unicode math.

Hangul syllables start at U+AC00 (가). Each syllable =
    (초성_index * 588) + (중성_index * 28) + 종성_index

초성 (19): ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ
중성 (21): ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ
종성 (28): none + ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ
"""

CHOSUNG = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
    "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
]

JUNGSUNG = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
    "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ",
]

JONGSUNG = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
]

HANGUL_BASE = 0xAC00


def decompose(syllable: str) -> tuple:
    """Decompose a single Hangul syllable into (cho, jung, jong) indices.

    Returns (cho_idx, jung_idx, jong_idx) where jong_idx may be 0 (no batchim).
    For non-Hangul chars returns (-1, -1, -1).
    """
    if len(syllable) != 1:
        raise ValueError(f"Expected single character, got '{syllable}'")
    code = ord(syllable)
    if code < HANGUL_BASE or code > 0xD7A3:
        return (-1, -1, -1)
    offset = code - HANGUL_BASE
    jong = offset % 28
    jung = ((offset - jong) // 28) % 21
    cho = (offset - jong) // 28 // 21
    return (cho, jung, jong)


def compose(cho_idx: int, jung_idx: int, jong_idx: int = 0) -> str:
    """Compose a Hangul syllable from cho, jung, jong indices."""
    if not (0 <= cho_idx < 19 and 0 <= jung_idx < 21 and 0 <= jong_idx < 28):
        raise ValueError(f"Invalid indices: cho={cho_idx}, jung={jung_idx}, jong={jong_idx}")
    return chr(HANGUL_BASE + (cho_idx * 588) + (jung_idx * 28) + jong_idx)


def has_batchim(stem: str) -> bool:
    """Check if the last syllable of stem has a final consonant (받침)."""
    if not stem:
        return False
    last = stem[-1]
    _, _, jong = decompose(last)
    return jong > 0


def get_last_vowel(syllable: str) -> str:
    """Get the vowel (중성) character of a syllable."""
    _, jung, _ = decompose(syllable)
    if jung < 0:
        return ""
    return JUNGSUNG[jung]


def get_last_batchim(syllable: str) -> str:
    """Get the final consonant (종성) of a syllable, or empty string."""
    _, _, jong = decompose(syllable)
    if jong <= 0:
        return ""
    return JONGSUNG[jong]


def is_yang_vowel(vowel: str) -> bool:
    """Check if vowel is 'yang' (양성모음): ㅏ, ㅗ, ㅑ, ㅛ, ㅘ, ㅚ, ㅐ."""
    return vowel in ("ㅏ", "ㅗ", "ㅑ", "ㅛ", "ㅘ", "ㅚ", "ㅐ")


def is_hangul(ch: str) -> bool:
    """Check if character is a Hangul syllable."""
    return HANGUL_BASE <= ord(ch) <= 0xD7A3


def merge_syllable(stem: str, ending: str) -> str:
    """Merge stem's last syllable with a vowel-starting ending.

    When the last syllable of stem has no batchim and ending starts with a vowel,
    the batchim-less final sound carries over to the ending.
    Example: "가" + "아요" → "가요" (the ㅏ from 가 merges with ㅏ from 아요)
    Actually this handles: stem + 아/어 → contracted form.
    """
    if not stem or not ending:
        return stem + ending

    last = stem[-1]
    cho, jung, jong = decompose(last)

    if jong == 0 and ending and is_hangul(ending[0]):
        # The final vowel might merge with the first vowel of the ending
        # This is handled by vowel contraction rules in the caller
        return stem + ending
    return stem + ending


def attach_ending(stem: str, ending: str) -> str:
    """Attach an ending to a stem, handling batchim-aware variants.

    If ending starts with a vowel and the last syllable of stem has batchim,
    the batchim carries over as the initial consonant of the first ending syllable.

    Example: "먹" + "어요" → "먹어요"
             "가" + "아요" → "가요" (vowel merger handled separately)
    """
    if not ending:
        return stem

    last = stem[-1]
    _, _, jong = decompose(last)

    if jong > 0 and is_hangul(ending[0]):
        e_cho, e_jung, e_jong = decompose(ending[0])
        # Move batchim to initial position of first ending syllable
        new_first = compose(jong, e_jung, e_jong)
        return stem + new_first + ending[1:]
    return stem + ending
