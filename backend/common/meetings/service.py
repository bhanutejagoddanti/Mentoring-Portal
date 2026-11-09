"""Common meeting service (shared scheduling utilities)."""
from __future__ import annotations

from common.database.repos.mentorship_repository import insert_meeting


def create_meeting(mentor_name: str, student_name: str, scheduled_at: str) -> dict:
    """Create a mentorship meeting record."""
    meeting = {'mentor': mentor_name, 'student': student_name, 'scheduled_at': scheduled_at, 'status': 'Scheduled'}
    insert_meeting(meeting)
    return {'status': 'created', 'meeting': meeting}
