"""OpenRouter LLM client (single responsibility: chat + embedding calls)."""
from __future__ import annotations

import json as _json
import re as _re


def _post_chat(messages: list[dict], temperature: float = 0.1, timeout: int = 30) -> dict | None:
    from config import config
    from flask import current_app

    if not config.OPENROUTER_API_KEY:
        return None
    try:
        import requests

        resp = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f"Bearer {config.OPENROUTER_API_KEY}",
                'Content-Type': 'application/json',
            },
            json={
                'model': config.OPENROUTER_MODEL,
                'messages': messages,
                'temperature': temperature,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        current_app.logger.warning('OpenRouter chat completion failed: %s', exc)
        return None


def openrouter_chat(prompt: str) -> dict | None:
    """Call the OpenRouter chat completion endpoint and return parsed JSON when available."""
    from flask import current_app

    data = _post_chat([
        {'role': 'system', 'content': 'You are an IIT Madras mentoring advisor. Extract factual professional profile facts as JSON. Return only valid JSON.'},
        {'role': 'user', 'content': prompt},
    ], temperature=0.1)
    if not data:
        return None
    try:
        content = data['choices'][0]['message']['content']
        content = _re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip())
        return _json.loads(content)
    except Exception as exc:
        current_app.logger.warning('OpenRouter JSON parse failed: %s', exc)
        return None


def openrouter_text(messages: list[dict], system: str = '', temperature: float = 0.4) -> str | None:
    """Conversational completion returning plain text (career assistant)."""
    full = ([{'role': 'system', 'content': system}] if system else []) + list(messages or [])
    data = _post_chat(full, temperature=temperature, timeout=40)
    if not data:
        return None
    try:
        return str(data['choices'][0]['message']['content'] or '').strip()
    except Exception:
        return None


def openrouter_embedding(text: str) -> list[float] | None:
    """Create a text embedding via OpenRouter for semantic mentor search."""
    from config import config
    from flask import current_app

    if not config.OPENROUTER_API_KEY or not (text or '').strip():
        return None
    try:
        import requests

        resp = requests.post(
            'https://openrouter.ai/api/v1/embeddings',
            headers={'Authorization': f"Bearer {config.OPENROUTER_API_KEY}", 'Content-Type': 'application/json'},
            json={'model': 'text-embedding-3-small', 'input': str(text)[:4000]},
            timeout=25,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data['data'][0]['embedding']
        current_app.logger.warning('OpenRouter embedding request returned %s: %s', resp.status_code, resp.text)
    except Exception as exc:
        current_app.logger.warning('OpenRouter embedding error: %s', exc)
    return None
