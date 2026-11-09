"""Vector store access (single responsibility: pgvector + app_state vectors)."""
from __future__ import annotations

from common.ai.matching import cosine_similarity
from common.database.state import get_state


def state_vectors() -> list[dict]:
    """Return mentors carrying precomputed vectors in app_state (source of truth)."""
    state = get_state()
    out = []
    for m in state.get('mentors') or []:
        v = m.get('vector')
        if isinstance(v, list) and len(v) == 1536:
            out.append(m)
    return out


def pgvector_top(query_vector: list[float], limit: int = 25) -> list[dict]:
    """Best-effort pgvector search via match_mentors RPC when tables exist.

    Returns list of {'mentor_name':..., 'similarity': float} — never raises.
    """
    if not query_vector:
        return []
    try:
        from extensions import sb
        res = sb.rpc('match_mentors', {'query_embedding': query_vector, 'match_count': limit}).execute()
        rows = getattr(res, 'data', None) or []
        counts = []
        for r in rows:
            try:
                counts.append({'mentor_id': r.get('mentor_id'), 'mentor_name': r.get('mentor_name') or r.get('name'), 'similarity': float(r.get('similarity') or 0.0)})
            except Exception:
                continue
        return counts
    except Exception as exc:
        try:
            from flask import current_app
            current_app.logger.warning('pgvector match_mentors fallback to cosine: %s', exc)
        except Exception:
            pass
        return []


def cosine_rank(query_vector: list[float], mentors: list[dict]) -> list[dict]:
    """Rank mentors by cosine similarity against precomputed vectors."""
    scored = []
    for m in mentors:
        v = m.get('vector')
        if not isinstance(v, list) or len(v) != len(query_vector):
            continue
        score = cosine_similarity(query_vector, v)
        scored.append({'mentor': m, 'score': round(float(score), 4)})
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored


def log_search(query: str, filters: dict, result_count: int, student_id: str | None = None) -> None:
    """Best-effort search audit log (never raises)."""
    try:
        from extensions import sb
        sb.table('mentor_search_logs').insert({'student_id': student_id, 'query': query, 'filters': filters or {}, 'result_count': result_count}).execute()
    except Exception:
        pass
