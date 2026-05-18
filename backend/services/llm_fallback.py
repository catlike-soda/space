"""DeepSeek API for sentence analysis.

DeepSeek: Chinese company, accessible in China without VPN.
Free credits on signup (5M tokens), then ¥1/1M tokens (~$0.14).
Get API key: https://platform.deepseek.com/api_keys
"""

import json
import hashlib
import os
import urllib.request
import urllib.error

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

_cache = {}


def _cache_key(sentence: str, ui_lang: str) -> str:
    return hashlib.md5((sentence + ui_lang).encode()).hexdigest()


def analyze_sentence(sentence: str, ui_lang: str = "ja") -> dict or None:
    """Analyze Korean sentence with DeepSeek. Returns structured JSON."""
    key = _cache_key(sentence, ui_lang)
    if key in _cache:
        return _cache[key]

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return None

    lang_name = "Japanese" if ui_lang == "ja" else "Chinese"

    if ui_lang == "ja":
        prompt = f"""韓国語を日本語文法で分析。語節数は入力と一致。JSONのみ出力：
"{sentence}"
{{"tokens":[{{"original":"語節","meaning":"意味","grammar":"文法（日本語文法と比較）"}}],"translation":"自然な日本語訳"}}"""
    else:
        prompt = f"""分析韩语句子，参照日语语法。语节数=输入。只输出JSON：
"{sentence}"
{{"tokens":[{{"original":"语节","meaning":"中文意思","grammar":"语法（参照日语语法对比说明）"}}],"translation":"中文翻译"}}"""

    try:
        req = urllib.request.Request(
            DEEPSEEK_URL,
            data=json.dumps({
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a Korean language analysis engine. Output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.0,
                "max_tokens": 512,
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )

        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

            result = json.loads(content)
            _cache[key] = result
            return result

    except Exception:
        return None
