"""Role authorization middleware: role gate."""
from __future__ import annotations

from functools import wraps

from flask import g, request


def roles(*allowed):
    """Decorator enforcing an authenticated session with an allowed role."""
    def deco(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            u = getattr(g, 'current_user', None)
            if u is None:
                u = getattr(request, 'current_user', None)
            if u is None:
                from common.auth.user import current_user as _cu
                u = _cu()
                if not u:
                    from common.responses import error_response
                    return error_response('Authentication required. Please sign in again.', 401)
                if not u.get('active', True):
                    from common.responses import error_response
                    return error_response('Account is deactivated. Contact IIC Admin.', 403)
                g.current_user = u
                request.current_user = u
            if u['role'] not in allowed:
                from common.responses import error_response
                return error_response(f"Insufficient permissions. Required role: {', '.join(allowed)}", 403)
            if not u.get('approved', True) and u['role'] == 'mentor':
                from common.responses import error_response
                return error_response('Your mentor account is pending IIC Admin approval.', 403)
            return fn(*args, **kwargs)
        return wrapped
    return deco
