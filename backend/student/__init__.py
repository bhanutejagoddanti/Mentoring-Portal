"""Student package (all features accessible via the Student dashboard)."""
from __future__ import annotations


def __getattr__(name):
    if name == 'student_bp':
        from student.routes import student_bp
        return student_bp
    raise AttributeError(name)


__all__ = ['student_bp']
