"""Admin user management service (student/mentor rosters + activation)."""
from __future__ import annotations

from common.database.state import get_state, save_state


def set_account_active(identifier: str, active: bool) -> dict:
    """Activate/deactivate a mentor account by id/name/email (state + auth profile)."""
    state = get_state()
    matched = False
    for m in state.get('mentors') or []:
        if str(m.get('id')) == str(identifier) or m.get('name') == identifier or m.get('email') == identifier:
            m['active'] = active
            matched = True
            if m.get('user_id'):
                try:
                    from extensions import sb
                    sb.table('user_profiles').update({'active': active}).eq('id', m['user_id']).execute()
                except Exception:
                    pass
    save_state(state)
    return {'message': 'Account status updated', 'active': active, 'matched': matched}


def roster() -> dict:
    """Students + mentors rosters for admin tables."""
    state = get_state()
    return {'students': state.get('students') or [], 'mentors': state.get('mentors') or []}
