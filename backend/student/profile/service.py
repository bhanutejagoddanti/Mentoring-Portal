"""Student profile & roster service (student dashboard: profile view)."""
from __future__ import annotations

from common.database.state import get_state


def list_students() -> list:
    """Return the student roster."""
    return list(get_state().get('students') or [])


def get_student(name: str) -> dict | None:
    """Return one student by name."""
    return next((s for s in get_state().get('students') or [] if s.get('name') == name), None)
