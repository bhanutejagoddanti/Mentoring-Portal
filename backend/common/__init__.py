"""Common package: genuinely shared functionality only.

Blueprints are exposed lazily via __getattr__ to avoid importing route
modules (which bind Supabase clients) before extensions.init_extensions().
"""
from __future__ import annotations


def __getattr__(name):
    if name == 'auth_bp':
        from common.auth import auth_bp
        return auth_bp
    if name == 'database_bp':
        from common.database.routes import bp
        return bp
    if name == 'communities_bp':
        from common.communities.routes import bp
        return bp
    if name == 'meetings_bp':
        from common.meetings.routes import bp
        return bp
    if name == 'notifications_bp':
        from common.notifications.routes import bp
        return bp
    raise AttributeError(name)


__all__ = ['auth_bp', 'database_bp', 'communities_bp', 'meetings_bp', 'notifications_bp']
