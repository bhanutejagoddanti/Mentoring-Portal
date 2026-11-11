"""Admin package (all features accessible via the IIC Admin dashboard)."""
from __future__ import annotations


def __getattr__(name):
    if name == 'admin_bp':
        from admin.routes import admin_bp
        return admin_bp
    if name == 'matching_bp_full':
        from admin.routes import matching_bp_full
        return matching_bp_full
    if name == 'help_status_bp_full':
        from admin.routes import help_status_bp_full
        return help_status_bp_full
    if name == 'community_moderation_bp':
        from admin.community_moderation.routes import bp
        return bp
    raise AttributeError(name)


__all__ = ['admin_bp', 'matching_bp_full', 'help_status_bp_full', 'community_moderation_bp']
