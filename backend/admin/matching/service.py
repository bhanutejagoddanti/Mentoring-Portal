"""Admin matching service (precomputed RAG indexing + re-indexing)."""
from __future__ import annotations

from common.ai import analyze_and_index_mentor
from common.database.state import get_state, save_state


def mentor_by_id(mentor_id: int) -> dict | None:
    """Return an approved mentor by numeric id."""
    state = get_state()
    return next((m for m in state.get('mentors', []) if int(m.get('id', -1)) == int(mentor_id) and m.get('approved') and m.get('active', True)), None)


def index_mentor(mentor_id: int) -> dict:
    """(Re)analyze + embed one approved mentor. Vectors are precomputed here,
    never regenerated during student search."""
    state = get_state()
    mentor = next((m for m in state.get('mentors', []) if int(m.get('id', -1)) == int(mentor_id) and m.get('approved') and m.get('active', True)), None)
    if not mentor:
        return {'error': 'Mentor not found', 'status': 404}
    if not mentor.get('approved'):
        return {'error': 'Approve mentor before generating semantic embeddings', 'status': 409}
    result = analyze_and_index_mentor(mentor)
    save_state(state)  # persist the SAME mutated state object
    return result


def ensure_indexed(latest_only: bool = False) -> dict:
    """Ensure every approved mentor has a precomputed vector; index missing ones once."""
    state = get_state()
    indexed_count = 0
    skipped = 0
    failed = 0
    for m in state.get('mentors') or []:
        if not (m.get('approved') and m.get('active', True)):
            skipped += 1
            continue
        if isinstance(m.get('vector'), list) and len(m['vector']) == 1536 and not latest_only:
            skipped += 1
            continue
        try:
            r = analyze_and_index_mentor(m)
            if r.get('has_embedding'):
                indexed_count += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    save_state(state)
    return {'indexed': indexed_count, 'skipped': skipped, 'failed': failed}
