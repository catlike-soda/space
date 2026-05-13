"""Seven Korean irregular verb/adjective type handlers.

Irregular types and how they transform when an ending starting with a vowel is attached:

  ㅂ → 우/오 : 춥다 → 추워요 (drop ㅂ, add 우 or 오 for 곱다/돕다)
  ㄷ → ㄹ    : 듣다 → 들어요 (change ㄷ to ㄹ)
  ㅅ → Ø     : 짓다 → 지어요 (drop ㅅ)
  르 → ㄹ라  : 다르다 → 달라요 (drop final 으, add ㄹ to previous syllable)
  ㄹ → Ø     : 살다 → 사세요 (ㄹ drops before ㄴ,ㅂ,ㅅ,ㅗ)
  ㅎ → Ø     : 그렇다 → 그래요 (ㅎ drops)
  으 → Ø     : 쓰다 → 써요 (으 drops, vowel harmony determines 아/어)
"""

from .jamo_utils import (decompose, compose, has_batchim, get_last_vowel,
                          get_last_batchim, CHOSUNG, JUNGSUNG, JONGSUNG)


def detect_irregular_type(dict_form: str, stem: str) -> str or None:
    """Auto-detect irregular type from dictionary form and stem.

    Args:
        dict_form: Full dictionary form like '춥다', '듣다'
        stem: Stem like '춥', '듣'

    Returns:
        Irregular type string or None if regular.
    """
    if not stem:
        return None

    last = stem[-1]
    _, _, jong = decompose(last)

    # 르 irregular
    if stem.endswith("르") and not has_batchim(stem[:-1]):
        return "르"

    # Check last syllable's batchim
    if jong > 0:
        batchim = JONGSUNG[jong]

        if batchim == "ㅂ":
            return "ㅂ"
        elif batchim == "ㄷ":
            return "ㄷ"
        elif batchim == "ㅅ":
            return "ㅅ"
        elif batchim == "ㄹ":
            # Only if the ending starts with certain consonants
            return "ㄹ"
        elif batchim == "ㅎ":
            return "ㅎ"

    # 으 irregular
    last_vowel = get_last_vowel(last)
    if last_vowel == "ㅡ":
        return "으"

    return None


def apply_irregular(stem: str, irr_type: str or None, ending: str) -> str:
    """Apply irregular transformation to stem before attaching ending.

    Args:
        stem: The verb/adjective stem
        irr_type: Irregular type or None
        ending: The ending to attach (first char determines handling)

    Returns:
        Transformed stem.
    """
    if irr_type is None or not ending:
        return stem

    if not ending or not _is_vowel_start(ending):
        # Most irregulars only apply before vowel-starting endings
        if irr_type in ("ㄹ", "으"):
            return _handle_special(stem, irr_type, ending)
        return stem

    if irr_type == "ㅂ":
        return _handle_bieup(stem)
    elif irr_type == "ㄷ":
        return _handle_digeut(stem)
    elif irr_type == "ㅅ":
        return _handle_siot(stem)
    elif irr_type == "르":
        return _handle_reu(stem)
    elif irr_type == "ㄹ":
        return _handle_rieul(stem, ending)
    elif irr_type == "ㅎ":
        return _handle_hieut(stem)
    elif irr_type == "으":
        return _handle_eu(stem, ending)
    return stem


def _is_vowel_start(ending: str) -> bool:
    """Check if ending starts with a vowel (including 아, 어, etc)."""
    if not ending:
        return False
    ch = ending[0]
    if ord(ch) < 0xAC00:
        return False
    cho, _, _ = decompose(ch)
    if cho < 0:
        return False
    return CHOSUNG[cho] == "ㅇ"


def _handle_bieup(stem: str) -> str:
    """ㅂ irregular: drop ㅂ, add 우 (or 오 for 돕다, 곱다)."""
    if not stem:
        return stem
    last = stem[-1]
    cho, jung, jong = decompose(last)

    # 돕다, 곱다 → 오; others → 우
    if cho == 3 and jung == 8:  # 도 or 고
        new_last = compose(cho, jung, 0)  # remove batchim
        return stem[:-1] + new_last + "오"
    else:
        new_last = compose(cho, jung, 0)
        return stem[:-1] + new_last + "우"


def _handle_digeut(stem: str) -> str:
    """ㄷ irregular: change ㄷ to ㄹ."""
    if not stem:
        return stem
    last = stem[-1]
    cho, jung, jong = decompose(last)
    if jong > 0 and JONGSUNG[jong] == "ㄷ":
        new_last = compose(cho, jung, 8)  # 8 = ㄹ batchim
        return stem[:-1] + new_last
    return stem


def _handle_siot(stem: str) -> str:
    """ㅅ irregular: drop ㅅ."""
    if not stem:
        return stem
    last = stem[-1]
    cho, jung, jong = decompose(last)
    if jong > 0 and JONGSUNG[jong] == "ㅅ":
        new_last = compose(cho, jung, 0)  # remove batchim
        return stem[:-1] + new_last
    return stem


def _handle_reu(stem: str) -> str:
    """르 irregular: drop 으 from 르, add ㄹ to previous syllable.

    다르다 → 달라요: 다 + 르 → 달 + 라
    """
    if not stem or not stem.endswith("르"):
        return stem
    base = stem[:-2]  # everything before "르"
    if base:
        prev = base[-1]
        p_cho, p_jung, p_jong = decompose(prev)
        if p_jong == 26:  # ㄹ already
            new_prev = compose(p_cho, p_jung, 0)
        else:
            # Add ㄹ as batchim to previous syllable
            new_prev = compose(p_cho, p_jung, 8)  # 8 = ㄹ
        return base[:-1] + new_prev + "라"
    return stem


def _handle_rieul(stem: str, ending: str) -> str:
    """ㄹ irregular: ㄹ drops before ㄴ, ㅂ, ㅅ, 오.

    살다 + 세요 → 사세요
    만들다 + 는 → 만드는 (ㄹ drops)
    """
    if not stem:
        return stem
    if not ending:
        return stem

    # Check if ending starts with ㄴ, ㅂ, ㅅ
    if is_hangul_syllable(ending[0]):
        e_cho, e_jung, e_jong = decompose(ending[0])
        e_cho_char = CHOSUNG[e_cho]
        if e_cho_char in ("ㄴ", "ㅂ", "ㅅ") or (e_cho_char == "ㅇ" and JUNGSUNG[e_jung] == "ㅗ"):
            # Drop ㄹ batchim
            last = stem[-1]
            cho, jung, jong = decompose(last)
            if jong > 0 and JONGSUNG[jong] == "ㄹ":
                new_last = compose(cho, jung, 0)
                return stem[:-1] + new_last
    return stem


def _handle_hieut(stem: str) -> str:
    """ㅎ irregular: ㅎ drops before vowel-starting endings.

    그렇다 → 그래요
    The batchim ㅎ disappears and the vowel determines 아/어.
    """
    if not stem:
        return stem
    last = stem[-1]
    cho, jung, jong = decompose(last)
    if jong > 0 and JONGSUNG[jong] == "ㅎ":
        new_last = compose(cho, jung, 0)
        return stem[:-1] + new_last
    return stem


def _handle_eu(stem: str, ending: str) -> str:
    """으 irregular: 으 drops, vowel harmony determines 아/어.

    쓰다 → 써요 (ㅡ→ㅓ)
    크다 → 커요
    예쁘다 → 예뻐요
    """
    if not stem:
        return stem
    last = stem[-1]
    cho, jung, jong = decompose(last)

    if JUNGSUNG[jung] == "ㅡ" and jong == 0:
        # 으 drops. Determine the replacement vowel (아/어) from previous syllable
        if len(stem) >= 2:
            prev = stem[-2]
            _, p_jung, _ = decompose(prev)
            prev_vowel = JUNGSUNG[p_jung]
            if prev_vowel in ("ㅏ", "ㅗ"):
                # 양성 → 아
                new_vowel_idx = 0  # ㅏ
            else:
                # 음성 → 어
                new_vowel_idx = 4  # ㅓ
        else:
            new_vowel_idx = 4  # ㅓ (default)

        new_last = compose(cho, new_vowel_idx, 0)
        return stem[:-1] + new_last
    return stem


def _handle_special(stem: str, irr_type: str, ending: str) -> str:
    """Handle irregulars that apply even before consonant-starting endings."""
    if irr_type == "ㄹ":
        return _handle_rieul(stem, ending)
    elif irr_type == "으":
        return _handle_eu(stem, ending)
    return stem


def is_hangul_syllable(ch: str) -> bool:
    """Check if character is a Hangul syllable block."""
    return 0xAC00 <= ord(ch) <= 0xD7A3


def extract_stem(dict_form: str) -> str:
    """Extract the stem from dictionary form (remove -다)."""
    if dict_form.endswith("다"):
        return dict_form[:-1]
    return dict_form
