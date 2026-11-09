"""Mentor package (all features accessible via the Mentor dashboard)."""
from __future__ import annotations


def __getattr__(name):
    if name == 'mentor_bp':
        from mentor.routes import mentor_bp
        return mentor_bp
    raise AttributeError(name)


__all__ = ['mentor_bp']
