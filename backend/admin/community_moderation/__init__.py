"""Admin community moderation package."""
from __future__ import annotations


def __getattr__(name):
    if name == 'community_moderation_bp':
        from admin.community_moderation.routes import bp
        return bp
    raise AttributeError(name)


__all__ = ['community_moderation_bp']
