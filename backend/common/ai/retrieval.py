"""Semantic retrieval + ranking + explanation (RAG search core).

- Embeds the student query ONCE per search (never re-embeds mentors).
- Prefers pgvector (match_mentors RPC) when available, else cosine over
  precomputed app_state vectors, else keyword overlap fallback.
- Applies eligibility + capacity + user filters before ranking.
- Builds a meaningful reason from ai_profile overlap + score.
"""
from __future__ import annotations

import re

from common.ai.embeddings import embed_query
from common.ai.vector_store import pgvector_top, cosine_rank, state_vectors, log_search
from common.database.state import get_state


def _words(query: str) -> set[str]:
    return {w for w in re.findall(r'[a-z0-9+#.]+', (query or '').lower()) if len(w) > 2}


def _assigned_counts() -> dict[str, int]:
    state = get_state()
    counts: dict[str, int] = {}
    for r in state.get('requests') or []:
        if r.get('status') == 'Accepted':
            counts[r.get('mentor')] = counts.get(r.get('mentor'), 0) + 1
    return counts


def is_eligible(mentor: dict, assigned: int) -> bool:
    """Eligibility + capacity gate."""
    if not mentor.get('approved') or not mentor.get('active', True):
        return False
    if mentor.get('available') is False:
        return False
    slots = mentor.get('slots')
    try:
        return int(slots or 0) > int(assigned or 0)
    except Exception:
        return False


def _pass_filters(mentor: dict, filters: dict) -> bool:
    field = filters.get('field') or ''
    industry = filters.get('industry') or ''
    mode = filters.get('mode') or ''
    if field and str(mentor.get('field') or '').lower() != str(field).lower():
        return False
    if industry and str(mentor.get('industry') or '').lower() != str(industry).lower():
        return False
    if mode and str(mentor.get('mode') or '').lower() != str(mode).lower():
        return False
    return True


def build_reason(mentor: dict, query: str, score: float = 0.0, method: str = "") -> str:
    """Short, natural student-facing reason grounded in actual profile data.

    Scores/methods stay internal (ranking only); never surfaced in the text.
    """
    qwords = _words(query)
    ai = mentor.get('ai_profile') or {}
    why_bits: list[str] = []
    for key, label in [('skills', 'skills'), ('mentoring_topics', 'topics they mentor on'), ('career_paths', 'career experience')]:
        terms = ai.get(key) or []
        hits = [str(t).strip() for t in terms if any(w in str(t).lower() for w in qwords)]
        if hits:
            why_bits.append(f"{label}: {', '.join(hits[:3])}")
    field = str(mentor.get('field') or '').strip()
    industry = str(mentor.get('industry') or '').strip()
    if field and field.lower() in (query or '').lower():
        why_bits.append(f"works in {field}")
    if industry and industry.lower() in (query or '').lower():
        why_bits.append(f"{industry} industry experience")
    if why_bits:
        return f"Great fit for what you're looking for — {'; '.join(why_bits)}."
    summary = str(ai.get('summary') or mentor.get('bio') or '').strip()
    if summary:
        return summary[:220]
    bits = [b for b in [field, industry, mentor.get('title') or mentor.get('role') or ''] if b]
    return f"A {bits[0]} professional" + (f" in {bits[1]}" if len(bits) > 1 else "") + " who can guide your next steps." if bits else "An approved mentor who can guide your next steps."


def _strip_vector(mentor: dict) -> dict:
    out = dict(mentor)
    out.pop('vector', None)
    return out


def semantic_search(query: str, filters: dict | None = None, limit: int = 5, user: dict | None = None) -> dict:
    """Return top mentors for a student query (max 5 recommended)."""
    filters = filters or {}
    limit = max(1, min(5, int(limit or 5)))
    state = get_state()
    assigned = _assigned_counts()
    eligible = [m for m in state.get('mentors') or [] if is_eligible(m, assigned.get(m.get('name'), 0)) and _pass_filters(m, filters)]

    q = (query or '').strip()
    qvec = embed_query(q) if q else None
    items: list[dict] = []
    method = 'keyword'
    if qvec:
        # 1) pgvector when relational tables exist (boosts matching rows by name).
        pg = pgvector_top(qvec, limit=limit * 5)
        method = 'pgvector' if pg else 'cosine'
        cosine = cosine_rank(qvec, eligible)
        # map pgvector names -> eligible mentors for boost (keep cosine as score if available)
        pg_names = {r['mentor_name']: r['similarity'] for r in pg if r.get('mentor_name')}
        for entry in cosine:
            m = entry['mentor']
            sim = pg_names.get(m.get('name'), entry['score'])
            items.append({'mentor': _strip_vector(m), '_score': round(float(max(entry['score'], sim or 0)), 4), 'reason': build_reason(m, q), 'match_explanation': build_reason(m, q)})
        # pgvector mentors that somehow lack app_state vectors
        if pg and not cosine:
            name_to_m = {m.get('name'): m for m in eligible}
            for r in pg:
                m = name_to_m.get(r.get('mentor_name'))
                if m and not any(i['mentor'].get('name') == m.get('name') for i in items):
                    items.append({'mentor': _strip_vector(m), '_score': r['similarity'], 'reason': build_reason(m, q), 'match_explanation': build_reason(m, q)})
        items.sort(key=lambda x: x.get('_score', 0), reverse=True)
    else:
        # No embedding available: keyword overlap fallback (still ranked, not hardcoded).
        qwords = _words(q)
        scored = []
        for m in eligible:
            hay = f"{m.get('field','')} {m.get('industry','')} {m.get('title','')} {m.get('role','')} {m.get('bio','')} {' '.join((m.get('ai_profile') or {}).get('skills') or [])} {' '.join((m.get('ai_profile') or {}).get('mentoring_topics') or [])}".lower()
            hits = sum(1 for w in qwords if w in hay)
            scored.append({'mentor': m, 'score': round(hits / max(1, len(qwords)), 3) if qwords else 0.5})
        scored.sort(key=lambda x: x['score'], reverse=True)
        for entry in scored:
            m = entry['mentor']
            items.append({'mentor': _strip_vector(m), '_score': entry['score'], 'reason': build_reason(m, q), 'match_explanation': build_reason(m, q)})
        method = 'keyword'

    items = items[:limit]
    log_search(q, filters, len(items), student_id=(user or {}).get('id') if user else None)
    for it in items:
        it.pop('_score', None)
    return {'items': items, 'total': len(items)}
