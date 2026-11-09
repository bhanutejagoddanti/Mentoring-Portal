"""Mentor RAG orchestrator (single responsibility: /find end-to-end workflow)."""
from __future__ import annotations

from common.ai.query_enhancer import enhance_query
from common.ai.retrieval import semantic_search


def _dedupe(items: list[dict], limit: int) -> list[dict]:
    seen = set()
    out = []
    for item in items:
        key = item.get('mentor', {}).get('id') or item.get('mentor', {}).get('name')
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
        if len(out) >= limit:
            break
    return out


def _expertise_line(mentor: dict) -> str:
    ai = mentor.get('ai_profile') or {}
    bits = [str(x).strip() for x in (ai.get('skills') or []) + (ai.get('mentoring_topics') or []) if str(x).strip()]
    field = str(mentor.get('field') or '').strip()
    industry = str(mentor.get('industry') or '').strip()
    expertise = bits[:4] or [b for b in [field, industry] if b]
    return ', '.join(expertise[:4]) if expertise else (field or 'career mentoring')


def top_explanation(item: dict, enhanced: dict | None = None, query: str = "") -> str:
    """Short natural first-mentor story grounded ONLY in retrieved profile data."""
    mentor = (item or {}).get('mentor') or {}
    name = mentor.get('name') or 'this mentor'
    title = mentor.get('title') or mentor.get('role') or ''
    ai = mentor.get('ai_profile') or {}
    summary = str(ai.get('summary') or mentor.get('bio') or '').strip()
    expertise = _expertise_line(mentor)
    lines = [f"We recommend {name} first."]
    if title:
        lines.append(f"{name} is a {title} whose experience covers {expertise}.")
    elif expertise:
        lines.append(f"Their background in {expertise} matches what you described.")
    if summary:
        lines.append(summary[:240])
    lines.append("They can help you plan projects, review your work and prepare for interviews in this area. Take a look at their profile to see if it fits your goals.")
    return ' '.join(lines)


def friendly_count(n: int) -> str:
    """Student-friendly count phrasing."""
    return 'We found 1 relevant mentor.' if n == 1 else f'We found {n} relevant mentors.'


def run_find(query: str, filters: dict | None = None, limit: int = 5, user: dict | None = None) -> dict:
    """Execute /find: enhance (internal) → embed once → RAG top 5 + explanation.

    Internal details (enhanced query, embeddings, scores, prompts) stay
    backend-only — only friendly text + mentor cards are returned.
    """
    raw = (query or '').strip()
    if not raw:
        return {'mode': 'clarification', 'reply': 'Sure — what kind of mentor are you looking for? For example: `/find mentor for Python and data science projects`.', 'message': 'Sure — what kind of mentor are you looking for? For example: `/find mentor for Python and data science projects`.', 'items': [], 'total': 0}
    enhanced = enhance_query(raw)
    search_query = enhanced.get('enhanced_query') or raw
    result = semantic_search(query=search_query, filters=filters or {}, limit=limit or 5, user=user)
    items = _dedupe(result.get('items') or [], limit or 5)
    if not items:
        msg = 'We could not find a strong match right now. Try broadening your skills, or remove tight filters and search again.'
        return {'mode': 'find', 'reply': msg, 'message': msg, 'items': [], 'total': 0}
    first = items[0]
    msg = friendly_count(len(items))
    return {
        'mode': 'find',
        'reply': msg,
        'message': msg,
        'items': items,
        'total': len(items),
        'first': first,
        'top_explanation': top_explanation(first, enhanced, raw),
    }
