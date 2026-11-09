"""Mentor repository (single responsibility: mentor reads/writes via app_state)."""
from __future__ import annotations


def list_mentors() -> list:
    """Read mentor records from the application state store."""
    from common.database.state import get_state

    state = get_state()
    return list(state.get('mentors') or [])


def insert_mentor(mentor: dict) -> None:
    """Persist a newly registered mentor into application state."""
    from common.database.state import get_state, save_state

    state = get_state()
    state.setdefault('mentors', []).append(mentor)
    save_state(state)
