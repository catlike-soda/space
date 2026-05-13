"""Revised Romanization of Korean."""

# Initial consonant romanization
CHO_ROM = {
    "ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt",
    "ㄹ": "r", "ㅁ": "m", "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s",
    "ㅆ": "ss", "ㅇ": "", "ㅈ": "j", "ㅉ": "jj", "ㅊ": "ch",
    "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h",
}

# Vowel romanization
JUNG_ROM = {
    "ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae", "ㅓ": "eo",
    "ㅔ": "e", "ㅕ": "yeo", "ㅖ": "ye", "ㅗ": "o", "ㅘ": "wa",
    "ㅙ": "wae", "ㅚ": "oe", "ㅛ": "yo", "ㅜ": "u", "ㅝ": "wo",
    "ㅞ": "we", "ㅟ": "wi", "ㅠ": "yu", "ㅡ": "eu", "ㅢ": "ui", "ㅣ": "i",
}

# Final consonant romanization
JONG_ROM = {
    "": "", "ㄱ": "k", "ㄲ": "k", "ㄳ": "k", "ㄴ": "n", "ㄵ": "n",
    "ㄶ": "n", "ㄷ": "t", "ㄹ": "l", "ㄺ": "k", "ㄻ": "m", "ㄼ": "l",
    "ㄽ": "l", "ㄾ": "l", "ㄿ": "p", "ㅀ": "l", "ㅁ": "m", "ㅂ": "p",
    "ㅄ": "p", "ㅅ": "t", "ㅆ": "t", "ㅇ": "ng", "ㅈ": "t", "ㅊ": "t",
    "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "t",
}


def romanize(text: str) -> str:
    """Convert Hangul text to Revised Romanization."""
    from .jamo_utils import decompose, CHOSUNG, JUNGSUNG, JONGSUNG, HANGUL_BASE

    result = []
    for ch in text:
        code = ord(ch)
        if code < HANGUL_BASE or code > 0xD7A3:
            result.append(ch)
            continue

        cho, jung, jong = decompose(ch)
        if cho < 0:
            result.append(ch)
            continue

        cho_char = CHOSUNG[cho]
        jung_char = JUNGSUNG[jung]
        jong_char = JONGSUNG[jong]

        rom = CHO_ROM.get(cho_char, "")
        rom += JUNG_ROM.get(jung_char, jung_char)
        rom += JONG_ROM.get(jong_char, "")
        result.append(rom)

    # No pronunciation change rules applied; this is basic romanization
    return "".join(result)
