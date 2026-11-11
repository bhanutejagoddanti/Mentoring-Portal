"""Shared messaging package (community chat + direct messaging services)."""
from __future__ import annotations

def __getattr__(name):
    if name == 'messaging_bp':
        from common.messaging.routes import bp
        return bp
    raise AttributeError(name)


__all__ = ['messaging_bp']
