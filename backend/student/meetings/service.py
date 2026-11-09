"""Student meeting service (student perspective: schedule + feedback)."""
from __future__ import annotations


def create_student_meeting(mentor_name: str, student_name: str, scheduled_at: str) -> dict:
    """Create a meeting record (state persistence in common/meetings route)."""
    from common.database.repos.mentorship_repository import insert_meeting
    meeting = {'mentor': mentor_name, 'student': student_name, 'scheduled_at': scheduled_at, 'status': 'Scheduled'}
    insert_meeting(meeting)
    return {'status': 'created', 'meeting': meeting}


def feedback_for(meeting_id: int) -> list:
    """Meeting feedback (reserved; stored on meeting payload)."""
    return []
