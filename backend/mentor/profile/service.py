"""Mentor profile service (credentials, expertise, capacity)."""
from __future__ import annotations

from common.database.state import get_state


def get_own(user: dict) -> dict | None:
    """Return the mentor record for the signed-in mentor."""
    state = get_state()
    return next((m for m in state.get('mentors') or [] if m.get('user_id') == user.get('id') or m.get('name') == user.get('name')), None)


def mentees(user: dict) -> list:
    """Return accepted mentorships for this mentor."""
    state = get_state()
    return [r for r in state.get('requests') or [] if r.get('mentor') == (user.get('name') or '') and r.get('status') == 'Accepted']
