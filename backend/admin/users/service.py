"""Admin user management service (student/mentor rosters + activation)."""
from __future__ import annotations

from common.database.state import get_state, save_state


def set_account_active(identifier: str, active: bool) -> dict:
    """Activate/deactivate a mentor account by id/name/email."""
    state = get_state()
    matched = False
    for m in state.get('mentors') or []:
        if str(m.get('id')) == str(identifier) or m.get('name') == identifier or m.get('email') == identifier:
            m['active'] = active
            matched = True
    save_state(state)
    return {'message': 'Account status updated', 'active': active, 'matched': matched}


def roster() -> dict:
    """Students + mentors rosters for admin tables."""
    state = get_state()
    return {'students': state.get('students') or [], 'mentors': state.get('mentors') or []}
