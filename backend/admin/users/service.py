"""Admin user management service (student/mentor rosters + activation)."""
from __future__ import annotations

import re

from common.database.state import get_state, save_state

_UUID_RE = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')


def set_account_active(identifier: str, active: bool) -> dict:
    """Activate/deactivate an account by id/name/email.

    Updates the synced app_state rosters and the authoritative auth profile so
    a deactivated account can no longer sign in (login checks user_profiles.active).
    """
    ident = str(identifier or '').strip()
    state = get_state()
    matched = False
    for key in ('mentors', 'students', 'users'):
        for item in state.get(key) or []:
            if (
                str(item.get('id')) == ident
                or item.get('name') == ident
                or (item.get('email') or '').lower() == ident.lower()
            ):
                item['active'] = active
                matched = True
    save_state(state)

    profile_updated = False
    try:
        from extensions import sb

        if '@' in ident:
            res = sb.table('user_profiles').update({'active': active}).eq('email', ident.lower()).execute()
        elif _UUID_RE.match(ident):
            res = sb.table('user_profiles').update({'active': active}).eq('id', ident).execute()
        else:
            res = sb.table('user_profiles').update({'active': active}).eq('name', ident).execute()
        profile_updated = bool(res.data)
    except Exception:
        profile_updated = False

    return {
        'message': 'Account status updated',
        'active': active,
        'matched': matched or profile_updated,
    }


def roster() -> dict:
    """Students + mentors rosters for admin tables."""
    state = get_state()
    return {'students': state.get('students') or [], 'mentors': state.get('mentors') or []}
