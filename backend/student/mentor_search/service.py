"""Student mentor search service (AI semantic search + manual filters)."""
from __future__ import annotations

from common.ai.retrieval import semantic_search as _semantic_search
from common.ai.matching import pass_search_filters
from common.database.state import get_state


def catalogue(field: str = '', query: str = '') -> list:
    """Approved, active mentors filtered for the student browser (full catalogue)."""
    mentors = [m for m in get_state().get('mentors', []) if m.get('approved') and m.get('active', True)]
    if field:
        mentors = [m for m in mentors if str(m.get('field', '')).lower() == field.lower()]
    if query:
        q = query.strip().lower()
        mentors = [m for m in mentors if q in (m.get('name') or '').lower()]
    return [_public(m) for m in mentors]


def filter_options() -> dict:
    """Distinct filter options for the student discovery UI."""
    mentors = [m for m in get_state().get('mentors', []) if m.get('approved') and m.get('active', True)]
    return {
        'fields': sorted({m.get('field', '') for m in mentors if m.get('field')}),
        'industries': sorted({m.get('industry', '') for m in mentors if m.get('industry')}),
        'modes': sorted({m.get('mode', '') for m in mentors if m.get('mode')}),
    }


def _public(mentor: dict) -> dict:
    out = dict(mentor)
    out.pop('vector', None)  # never leak raw embeddings to clients
    return out


def semantic_search(query: str, filters: dict | None = None, limit: int = 5, user: dict | None = None) -> dict:
    """Top mentors for a career query (embeds query once; mentor vectors precomputed)."""
    # Delegate to shared RAG core; strip vectors defensively.
    result = _semantic_search(query=query, filters=filters or {}, limit=limit or 5, user=user)
    for item in result.get('items', []):
        item['mentor'] = _public(item.get('mentor') or {})
    return result


def keyword_search(field: str = '', limit: int = 20) -> list:
    """Backwards-compatible helper: ranked fallback (no embeddings)."""
    mentors = [m for m in get_state().get('mentors') or [] if m.get('approved') and m.get('active', True) and pass_search_filters(m, {'field': field})]
    return [{'mentor': _public(m), 'score': 0.5, 'reason': 'Catalogue match'} for m in mentors[:limit]]
