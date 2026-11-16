"""Shared meeting routes (list + create; role-specific services live in student/mentor)."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.responses import api_response, error_response
from common.database.state import get_state, save_state

bp = Blueprint('common_meetings', __name__, url_prefix='/api/meetings')


@bp.get('')
@login_required
def list_meetings():
    """List meetings visible to the current user."""
    u = current_user()
    items = list(get_state().get('meetings') or [])
    for m in items:  # normalize legacy frontend `date` key to `scheduled_at`
        if not m.get('scheduled_at') and m.get('date'):
            m['scheduled_at'] = m['date']
        if not m.get('date') and m.get('scheduled_at'):
            m['date'] = m['scheduled_at']
    if u.get('role') != 'admin':
        items = [m for m in items if m.get('mentor') == u.get('name') or m.get('student') == u.get('name')]
    return api_response(items=items, total=len(items))


@bp.post('')
@login_required
def create_meeting_route():
    """Create a meeting (delegates to role-aware meeting service)."""
    data = request.get_json() or {}
    mentor = (data.get('mentor') or '').strip()
    student = (data.get('student') or '').strip()
    scheduled_at = (data.get('scheduled_at') or data.get('date') or '').strip()
    if not mentor or not student or not scheduled_at:
        return error_response('mentor, student and scheduled_at are required', 400)
    from student.meetings.service import create_student_meeting
    result = create_student_meeting(mentor, student, scheduled_at)
    state = get_state()
    state.setdefault('meetings', []).append(result['meeting'])
    save_state(state)
    return api_response(result, status=201)
