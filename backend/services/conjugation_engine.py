"""Korean conjugation engine orchestrator.

Generates all conjugation forms for a verb or adjective:
  4 speech levels x 4 moods x 3 tenses (+ optional honorific) = 48+ forms.
"""

from .speech_levels import SPEECH_LEVELS, MOODS, TENSES, LEVEL_ORDER, YANG_VOWELS
from .irregular_handler import (apply_irregular, detect_irregular_type,
                                extract_stem, is_hangul_syllable, _is_vowel_start)
from .jamo_utils import (decompose, compose, has_batchim, get_last_vowel,
                          get_last_batchim, CHOSUNG, JUNGSUNG, JONGSUNG)
from .romanization import romanize


class ConjugationEngine:
    """Generates all conjugation forms for a given word."""

    def __init__(self, hangul: str, word_type: str, irregular_type: str = None,
                 stem: str = None):
        """
        Args:
            hangul: Dictionary form (e.g., '가다', '먹다')
            word_type: 'verb' or 'adjective'
            irregular_type: One of 'ㅂ','ㄷ','ㅅ','르','ㄹ','ㅎ','으' or None
            stem: Pre-computed stem. Extracted from hangul if not provided.
        """
        self.hangul = hangul
        self.word_type = word_type
        self.irregular_type = irregular_type
        self.stem = stem or extract_stem(hangul)

        # Auto-detect irregular type if not provided
        if self.irregular_type is None and hangul.endswith("다"):
            detected = detect_irregular_type(hangul, self.stem)
            if detected:
                self.irregular_type = detected

    def generate_all(self, honorific: bool = False) -> list:
        """Generate all conjugation forms.

        Returns a list of dicts, each with:
            speech_level, mood, tense, honorific, conjugated, pronunciation,
            level_name_kr, level_name_zh
        """
        results = []
        for level in LEVEL_ORDER:
            level_config = SPEECH_LEVELS[level]
            for mood in MOODS:
                moods_dict = level_config.get(mood, {})
                for tense in TENSES:
                    ending_pair = moods_dict.get(tense)
                    if ending_pair is None:
                        continue

                    conjugated = self.conjugate(level, mood, tense, honorific)
                    if conjugated:
                        results.append({
                            "speech_level": level,
                            "level_name_kr": level_config.get("name_kr", level),
                            "level_name_zh": level_config.get("name_zh", level),
                            "mood": mood,
                            "tense": tense,
                            "honorific": honorific,
                            "conjugated": conjugated,
                            "pronunciation": romanize(conjugated),
                        })
        return results

    def conjugate(self, speech_level: str, mood: str, tense: str,
                  honorific: bool = False) -> str:
        """Conjugate a single form.

        Returns the conjugated Hangul string.
        """
        stem = self.stem

        # Apply honorific infix -시- before the ending
        if honorific:
            stem = self._apply_honorific(stem)

        # Get the ending pair (has_batchim, no_batchim)
        level_config = SPEECH_LEVELS.get(speech_level, {})
        mood_config = level_config.get(mood, {})
        ending_pair = mood_config.get(tense)
        if ending_pair is None:
            return ""

        # Handle 하다 special case → 여
        if self._is_hada():
            return self._conjugate_hada(speech_level, mood, tense, honorific, ending_pair)

        # Apply irregular transformation to stem
        transformed_stem = apply_irregular(stem, self.irregular_type,
                                           ending_pair[0])

        # Resolve vowel harmony (아/어 choice)
        ending = self._resolve_ending(transformed_stem, ending_pair)

        # Handle 으 irregular vowel merger
        if self.irregular_type == "으" and ending:
            transformed_stem = apply_irregular(stem, "으", ending)

        # Handle ㄹ irregular before endings starting with certain consonants
        if self.irregular_type == "ㄹ" and ending:
            transformed_stem = apply_irregular(stem, "ㄹ", ending)

        # Attach ending, handling batchim carryover
        result = self._attach(transformed_stem, ending)

        return result

    def _is_hada(self) -> bool:
        """Check if this is a 하다 verb/adjective."""
        return self.stem == "하"

    def _conjugate_hada(self, speech_level: str, mood: str, tense: str,
                        honorific: bool, ending_pair: tuple) -> str:
        """Handle 하다 special conjugation → 해/하여."""
        stem = "하시" if honorific else "하"

        # 하 + 아/어 → 해 (하여 in formal)
        if speech_level == "formal_polite":
            yeo_stem = "하셨" if honorific else "하였"
            # Use 여 form
            if tense == "present":
                if mood == "declarative":
                    return yeo_stem[:-1] + "습니다"
                elif mood == "interrogative":
                    return yeo_stem[:-1] + "습니까"
                elif mood == "imperative":
                    base = "하십시오" if not honorific else "하십시오"
                    return base
                elif mood == "propositive":
                    return "합시다" if not honorific else "하십시다"
            elif tense == "past":
                return yeo_stem + "습니다" if mood != "interrogative" else yeo_stem + "습니까"
            elif tense == "future":
                base = "하겠" if not honorific else "하시겠"
                return base + "습니다" if mood != "interrogative" else base + "습니까"
            return stem

        # For other speech levels, 하 + 아/어 → 해
        hae = "하셔" if honorific else "해"

        if speech_level == "informal_polite":
            suffix = "요"
            if tense == "present":
                return hae + suffix
            elif tense == "past":
                base = "하셨어" if honorific else "했어"
                return base + suffix
            elif tense == "future":
                base = "하시겠어" if honorific else "하겠어"
                return base + suffix

        elif speech_level == "informal_casual":
            if tense == "present":
                return hae
            elif tense == "past":
                return "하셨어" if honorific else "했어"
            elif tense == "future":
                return "하시겠어" if honorific else "하겠어"

        elif speech_level == "formal_neutral":
            if tense == "present":
                return hae + "요"  # simplified
            # Simplified for 하오체

        return stem

    def _apply_honorific(self, stem: str) -> str:
        """Apply -시- honorific infix to the stem.

        시 follows a consonant-ending stem; if stem ends in vowel, 시 attaches directly.
        Example: 가다 → 가시다, 먹다 → 먹으시다 → 드시다 (irregular)
        """
        # Common honorific exceptions
        HONORIFIC_EXCEPTIONS = {
            "있": "계시",  # 있다 → 계시다
            "없": "없으시",  # 없다 → 없으시다 (regular for 시)
            "먹": "드시",  # 먹다 → 드시다
            "마시": "드시",  # 마시다 → 드시다
            "자": "주무시", # 자다 → 주무시다
            "말하": "말씀하시",  # 말하다 → 말씀하시다
        }

        # Check if stem is in exception list
        for key, val in HONORIFIC_EXCEPTIONS.items():
            if stem.startswith(key) or stem == key:
                return val

        if has_batchim(stem):
            return stem + "으시"
        else:
            return stem + "시"

    def _resolve_ending(self, stem: str, ending_pair: tuple) -> str:
        """Choose the right ending variant based on batchim and vowel harmony.

        ending_pair is (has_batchim_variant, no_batchim_variant) or
                        (yin_vowel_variant, yang_vowel_variant).
        For 아/어 pairs, the first is 어 (yin) and second is 아 (yang).
        """
        has_bat = has_batchim(stem)

        # Simple batchim-based choice (e.g., 습니다/ㅂ니다)
        if has_bat:
            first, second = ending_pair
            # Check if the pair is batchim-based or vowel-harmony based
            if second and second[0] in ("ㅂ", "습", "으", "세"):
                return first
            if second and len(second) >= 1:
                # Might be 아/어 pair
                if "아" in second or "았" in second:
                    # Vowel harmony choice
                    return self._vowel_harmony_ending(stem, ending_pair)
            return first
        else:
            # No batchim
            first, second = ending_pair
            if first and second and len(first) >= 1 and len(second) >= 1:
                # If starts with ㅂ (choice between 습/ㅂ), pick second for no batchim
                if second[0] in ("ㅂ", "십", "ㅂ시"):
                    return second
                # 아/어 pair
                if "아" in second or "았" in second:
                    return self._vowel_harmony_ending(stem, ending_pair)
            return second if second else first

    def _vowel_harmony_ending(self, stem: str, ending_pair: tuple) -> str:
        """Choose 아 (yang) or 어 (yin) ending based on stem's last vowel."""
        if not stem:
            return ending_pair[0]

        last_vowel = get_last_vowel(stem[-1])
        if not last_vowel:
            # Check previous syllable for 으 irregular
            if len(stem) >= 2:
                last_vowel = get_last_vowel(stem[-2])

        if last_vowel in YANG_VOWELS:
            return ending_pair[1]  # 아 variant
        else:
            return ending_pair[0]  # 어 variant

    def _attach(self, stem: str, ending: str) -> str:
        """Attach ending to stem with proper Hangul syllable adjustments."""
        if not ending:
            return stem

        # If ending starts with ㅂ or 습/습 format and stem has batchim
        if ending.startswith("습") or ending.startswith("습니") or ending.startswith("습니까"):
            if has_batchim(stem):
                return stem + ending
            else:
                return stem + ending  # already resolved by caller

        # Handle vowel-starting endings
        if _is_vowel_start(ending) and stem:
            last = stem[-1]
            cho, jung, jong = decompose(last)

            if jong == 0:
                # No batchim: vowel merges. The ending's initial ㅇ is replaced
                # by nothing (vowel contraction).
                # Example: 가 + 아 → 가 (ㅏ + ㅏ → ㅏ), but in practice:
                # 가 + 아요 → 가요 (just drop the ㅇ-based syllable's consonant)
                e_cho, e_jung, e_jong = decompose(ending[0])
                # If both vowels are the same, they merge
                prev_vowel = JUNGSUNG[jung]
                end_vowel = JUNGSUNG[e_jung]
                if prev_vowel == end_vowel:
                    # Same vowel, merge: 가 + 아 → 가
                    merged = compose(cho, jung, e_jong)
                    return stem[:-1] + merged + ending[1:]
                elif prev_vowel == "ㅏ" and end_vowel == "ㅓ":
                    # ㅏ + ㅓ → ㅐ (non-standard but seen in some contractions)
                    return stem + ending
                elif prev_vowel == "ㅗ" and end_vowel == "ㅏ":
                    # ㅗ + ㅏ → ㅘ
                    wa_idx = 9  # ㅘ
                    merged = compose(cho, wa_idx, e_jong)
                    return stem[:-1] + merged + ending[1:]
                elif prev_vowel == "ㅜ" and end_vowel == "ㅓ":
                    # ㅜ + ㅓ → ㅝ
                    weo_idx = 13  # ㅝ
                    merged = compose(cho, weo_idx, e_jong)
                    return stem[:-1] + merged + ending[1:]
                else:
                    # Different vowels, just drop the ㅇ and attach
                    return stem + ending
            else:
                # Has batchim: batchim carries over as initial consonant
                return stem + ending

        return stem + ending
