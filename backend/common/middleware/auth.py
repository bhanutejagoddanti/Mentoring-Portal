"""Authentication middleware: login gate."""
from __future__ import annotations

from functools import wraps

from flask import request

from common.auth.user import current_user
from common.responses import error_response


def login_required(fn):
    """Decorator enforcing an authenticated, active session."""
    @wraps(fn)
    def wrapped(*args, **kwargs):
        u = current_user()
        if not u:
            return error_response('Authentication required. Please sign in again.', 401)
        if not u.get('active', True):
            return error_response('Account is deactivated. Contact IIC Admin.', 403)
        # attached storage key name (no Flask attr mutation via request object in helpers style)
        from flask import g
        g.current_user = u
        return fn(*args, **kwargs)
    return wrapped
