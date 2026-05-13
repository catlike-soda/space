"""Free LLM API for sentence analysis using Google Gemini Flash.

Gemini Flash 2.0: free forever, 1,500 requests/day, no credit card.
Get API key: https://aistudio.google.com/apikey
"""

import json
import hashlib
import os
import urllib.request
import urllib.error

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

_cache = {}


def _cache_key(sentence: str) -> str:
    return hashlib.md5(sentence.encode()).hexdigest()


def analyze_sentence(sentence: str, ui_lang: str = "ja") -> dict or None:
    """Send sentence to Gemini Flash for grammar analysis. Free forever.

    Args:
        sentence: Korean sentence to analyze
        ui_lang: 'ja' for Japanese, 'zh' for Chinese

    Returns parsed JSON dict if successful, None otherwise.
    """
    key = _cache_key(sentence + ui_lang)
    if key in _cache:
        return _cache[key]

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None

    lang_instruction = "Japanese" if ui_lang == "ja" else "Chinese"

    prompt = f"""Analyze this Korean sentence as a language teacher. Output ONLY valid JSON:

"{sentence}"

{{
  "tokens": [
    {{
      "original": "Korean word/chunk",
      "dictionary_form": "dictionary form or null",
      "meaning": "meaning in {lang_instruction}",
      "grammar_role": "subject/object/verb/adjective/adverb/particle/etc"
    }}
  ],
  "grammar_points": [
    {{
      "pattern": "grammar pattern in Korean",
      "explanation": "explanation in {lang_instruction}"
    }}
  ],
  "translation": "full translation in {lang_instruction}"
}}"""

    try:
        req = urllib.request.Request(
            f"{GEMINI_API_URL}?key={api_key}",
            data=json.dumps({
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1024,
                }
            }).encode(),
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            content = data["candidates"][0]["content"]["parts"][0]["text"]

            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            result = json.loads(content)
            _cache[key] = result
            return result

    except Exception:
        return None
