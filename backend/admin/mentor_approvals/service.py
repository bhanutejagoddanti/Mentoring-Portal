"""Mentor approval service (verify + approve + auto-index for RAG)."""
from __future__ import annotations

from common.ai import analyze_and_index_mentor
from common.database.state import get_state, save_state


def approve_mentor(mentor_id: int) -> dict:
    """Approve a mentor and immediately analyze + embed their profile.

    Indexing is best-effort: approval succeeds even if the LLM/embeddings
    call fails, but the result reports has_embedding so the admin can
    re-index explicitly via POST /api/mentors/<id>/index.
    """
    state = get_state()
    mentor = next((m for m in state.get('mentors') or [] if int(m.get('id', -1)) == int(mentor_id)), None)
    if not mentor:
        return {'error': 'Mentor not found', 'status': 404}
    mentor['approved'] = True
    mentor['active'] = True
    indexed: dict = {}
    try:
        indexed = analyze_and_index_mentor(mentor)
    except Exception as exc:  # never block approval on AI outage
        try:
            from flask import current_app
            current_app.logger.warning('Approval indexing deferred for mentor %s: %s', mentor_id, exc)
        except Exception:
            pass
        indexed = {'indexed': False, 'has_embedding': False, 'error': str(exc)[:300]}
    save_state(state)
    return {'status': 'approved', 'mentor': mentor, 'indexing': indexed}
