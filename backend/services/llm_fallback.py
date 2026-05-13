"""LLM API fallback for complex sentence analysis.

Uses DeepSeek Chat (free tier) for unresolved grammar analysis.
Caches results to avoid repeat API calls.
"""

import json
import hashlib
import os
import urllib.request
import urllib.error

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Simple in-memory cache (survives within a single process)
_cache = {}


def _cache_key(sentence: str) -> str:
    return hashlib.md5(sentence.encode()).hexdigest()


def analyze_sentence(sentence: str) -> dict or None:
    """Send sentence to LLM for detailed grammar analysis.

    Returns parsed JSON dict if successful, None otherwise.
    """
    key = _cache_key(sentence)
    if key in _cache:
        return _cache[key]

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return None

    prompt = f"""You are a Korean language teacher. Analyze this Korean sentence thoroughly:
"{sentence}"

Return ONLY a JSON object (no markdown, no explanation) with this structure:
{{
  "tokens": [
    {{
      "original": "the original word/chunk in Korean",
      "dictionary_form": "base dictionary form if it's a verb/adjective, otherwise null",
      "meaning_zh": "Chinese meaning of this token",
      "grammar_role": "subject/object/verb/adjective/adverb/etc"
    }}
  ],
  "grammar_points": [
    {{
      "pattern": "the grammar pattern used (Korean)",
      "explanation_zh": "explanation in Chinese"
    }}
  ],
  "translation_zh": "complete Chinese translation of the sentence"
}}"""

    try:
        req = urllib.request.Request(
            DEEPSEEK_API_URL,
            data=json.dumps({
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a Korean language analysis engine. Always output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 1024,
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            content = data["choices"][0]["message"]["content"]

            # Try to extract JSON from response
            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            result = json.loads(content)
            _cache[key] = result
            return result

    except (urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError) as e:
        return None
    except Exception:
        return None
