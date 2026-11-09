"""Authentication helpers (bearer token + current user resolution)."""
from __future__ import annotations

from flask import request

from common.database.profile import get_profile


def bearer_token() -> str | None:
    """Extract the bearer token from the current request."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.lower().startswith('bearer '):
        return auth_header[7:].strip()
    return None


def current_user() -> dict | None:
    """Resolve the authenticated user from the bearer token and profile row."""
    from extensions import auth_client

    token = bearer_token()
    if not token:
        return None
    try:
        res = auth_client.auth.get_user(token)
        au = res.user
        if not au:
            return None
        p = get_profile(au.id)
        if not p:
            meta = au.user_metadata or {}
            return {'id': au.id, 'email': au.email, 'name': meta.get('name', 'User'), 'role': meta.get('role', 'student'), 'approved': True, 'active': True}
        return {
            'id': au.id, 'email': au.email,
            'name': p.get('name') or au.user_metadata.get('name', 'User'),
            'role': p.get('role', 'student'),
            'approved': p.get('approved', True), 'active': p.get('active', True),
        }
    except Exception:
        return None
