"""Mentor meeting service (session notes & outcomes live on meeting payloads)."""
from __future__ import annotations

from common.database.state import get_state


def for_mentor(user: dict) -> list:
    """Meetings where this user is the mentor."""
    return [m for m in get_state().get('meetings') or [] if m.get('mentor') == user.get('name')]
