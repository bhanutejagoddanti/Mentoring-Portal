"""Shared meeting routes (list + create; role-specific services live in student/mentor)."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.responses import api_response
from common.database.state import get_state, save_state

bp = Blueprint('common_meetings', __name__, url_prefix='/api/meetings')


@bp.get('')
@login_required
def list_meetings():
    """List meetings visible to the current user."""
    u = current_user()
    items = list(get_state().get('meetings') or [])
    if u.get('role') != 'admin':
        items = [m for m in items if m.get('mentor') == u.get('name') or m.get('student') == u.get('name')]
    return api_response(items=items, total=len(items))


@bp.post('')
@login_required
def create_meeting_route():
    """Create a meeting (delegates to role-aware meeting service)."""
    data = request.get_json() or {}
    from student.meetings.service import create_student_meeting
    result = create_student_meeting(data.get('mentor') or '', data.get('student') or '', data.get('scheduled_at') or '')
    try:
        state = get_state()
        state.setdefault('meetings', []).append({
            'id': None, 'mentor': data.get('mentor') or '', 'student': data.get('student') or '',
            'scheduled_at': data.get('scheduled_at') or '', 'status': 'Scheduled',
        })
        save_state(state)
    except Exception:
        pass
    return api_response(result, status=201)
