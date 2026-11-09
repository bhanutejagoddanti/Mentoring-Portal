"""Common database package (lazy to avoid import cycles)."""
from __future__ import annotations


def __getattr__(name):
    if name == 'database_bp':
        from common.database.routes import bp
        return bp
    raise AttributeError(name)


__all__ = ['database_bp']
