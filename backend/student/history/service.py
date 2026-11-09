"""Student history service (past mentorship terms)."""
from __future__ import annotations

from common.database.state import get_state


def history_for(student_id: int) -> list:
    """Return mentorship history for a student (currently empty by design)."""
    return []
