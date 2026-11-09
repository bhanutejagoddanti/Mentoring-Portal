"""Mentorship repository for the IITM BS Mentoring Portal backend."""
from __future__ import annotations

from extensions import sb


def insert_request(request: dict) -> None:
    """Persist a mentorship request."""
    sb.table('mentorship_requests').insert({
        'student_id': request.get('student_id'),
        'student_name': request.get('student'),
        'mentor_name': request.get('mentor'),
        'goal': request.get('goal'),
        'message': request.get('message'),
        'status': request.get('status', 'Pending'),
        'term': request.get('term'),
    }).execute()


def insert_meeting(meeting: dict) -> None:
    """Persist a mentorship meeting record."""
    sb.table('meetings').insert(meeting).execute()
