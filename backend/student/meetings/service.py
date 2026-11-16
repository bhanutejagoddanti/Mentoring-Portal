"""Student meeting service (student perspective: schedule + feedback)."""
from __future__ import annotations

import time


def create_student_meeting(mentor_name: str, student_name: str, scheduled_at: str) -> dict:
    """Build a meeting record (the shared route persists it in app_state)."""
    meeting = {
        'id': int(time.time() * 1000),
        'mentor': mentor_name,
        'student': student_name,
        'scheduled_at': scheduled_at,
        'date': scheduled_at,
        'status': 'Scheduled',
    }
    return {'status': 'created', 'meeting': meeting}


def feedback_for(meeting_id: int) -> list:
    """Meeting feedback (reserved; stored on meeting payload)."""
    return []
