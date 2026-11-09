"""User repository for the IITM BS Mentoring Portal backend."""
from __future__ import annotations

from extensions import sb


def get_user_profile(user_id: str) -> dict | None:
    """Fetch a user profile row by Supabase auth user id."""
    r = sb.table('user_profiles').select('*').eq('id', user_id).limit(1).execute()
    return r.data[0] if r.data else None


def update_user_profile(user_id: str, updates: dict) -> None:
    """Update a user profile row."""
    sb.table('user_profiles').update(updates).eq('id', user_id).execute()
