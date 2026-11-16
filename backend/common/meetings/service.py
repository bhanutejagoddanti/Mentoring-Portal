"""Common meeting service (shared scheduling utilities)."""
from __future__ import annotations

import time


def create_meeting(mentor_name: str, student_name: str, scheduled_at: str) -> dict:
    """Build a mentorship meeting record (persisted by the shared route)."""
    meeting = {
        'id': int(time.time() * 1000),
        'mentor': mentor_name,
        'student': student_name,
        'scheduled_at': scheduled_at,
        'date': scheduled_at,
        'status': 'Scheduled',
    }
    return {'status': 'created', 'meeting': meeting}
