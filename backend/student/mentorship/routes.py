"""Student mentorship routes (formal requests with preferences)."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.middleware.role import roles
from common.responses import api_response
from common.database.state import get_state, save_state
from student.mentorship.service import create_request, list_requests

bp = Blueprint('student_mentorship', __name__)


@bp.get('')
@login_required
def list_mentorship_requests():
    """List mentorship requests (admins see all)."""
    u = current_user()
    items = list_requests()
    if u.get('role') != 'admin':
        items = [r for r in items if r.get('email') == u.get('email') or r.get('student') == u.get('name')]
    return api_response(items=items, total=len(items))


@bp.post('')
@login_required
def create_mentorship_request():
    """Create a formal mentorship request (goal, message, optional preferences)."""
    u = current_user()
    data = request.get_json() or {}
    result = create_request(
        student_name=u.get('name') or '', student_email=u.get('email') or '',
        mentor_name=data.get('mentor') or '', goal=data.get('goal') or '',
        message=data.get('message') or '', term='Sep–Dec 2026',
        preferences=data.get('preferences') or data.get('selected_mentors') or [],
    )
    if result.get('error'):
        return api_response(result, status=result.get('status', 400), error=result.get('error'))
    return api_response(result, status=201)


@bp.post('/<int:req_id>/<decision>')
@roles('admin')
def decide_mentorship_request(req_id: int, decision: str):
    """Admin decision endpoint for mentorship requests."""
    state = get_state()
    req = next((r for r in state.get('requests') or [] if int(r.get('id', -1)) == int(req_id)), None)
    if not req:
        return api_response({'error': 'Request not found'}, status=404)
    req['status'] = 'Accepted' if decision == 'Approved' else 'Rejected'
    save_state(state)
    return api_response({'status': 'updated', 'request': req})
