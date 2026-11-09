"""Mentor availability service (capacity & slots)."""
from __future__ import annotations

from common.database.state import get_state

def capacity(user: dict) -> dict:
    """Return slots/assigned counts for this mentor."""
    state = get_state()
    mentor = next((m for m in state.get('mentors') or [] if m.get('name') == user.get('name')), None)
    if not mentor:
        return {'slots': 0, 'assigned': 0}
    assigned = sum(1 for r in state.get('requests') or [] if r.get('mentor') == mentor.get('name') and r.get('status') == 'Accepted')
    return {'slots': mentor.get('slots') or 0, 'assigned': assigned}
