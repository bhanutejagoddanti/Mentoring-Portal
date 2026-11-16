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
    """Persist a mentorship meeting record (maps state keys to table columns)."""
    sb.table('meetings').insert({
        'student_name': meeting.get('student'),
        'mentor_name': meeting.get('mentor'),
        'scheduled_at': meeting.get('scheduled_at') or meeting.get('date'),
        'status': meeting.get('status', 'Scheduled'),
        'meeting_link': meeting.get('meeting_link'),
        'notes': meeting.get('notes'),
    }).execute()
