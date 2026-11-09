"""Mentor mentorship service (match requests: preview/decide helpers)."""
from __future__ import annotations

from common.database.state import get_state


def pending_for(user: dict) -> list:
    """Pending mentorship requests addressed to this mentor."""
    state = get_state()
    return [r for r in state.get('requests') or [] if r.get('mentor') == user.get('name') and r.get('status') == 'Pending']
