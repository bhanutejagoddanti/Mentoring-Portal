"""Shared user profile reads (user_profiles)."""
from __future__ import annotations

from flask import current_app


def get_profile(user_id: str):
    """Fetch the role/approval profile row for a Supabase user id."""
    from extensions import sb
    try:
        r = sb.table('user_profiles').select('*').eq('id', user_id).limit(1).execute()
        return r.data[0] if r.data else None
    except Exception as exc:
        current_app.logger.error('Error fetching user profile %s: %s', user_id, exc)
        return None


def update_profile(user_id: str, updates: dict) -> None:
    """Update a user profile row (used by admin user management)."""
    from extensions import sb
    sb.table('user_profiles').update(updates).eq('id', user_id).execute()
