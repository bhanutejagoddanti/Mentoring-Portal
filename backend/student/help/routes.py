"""Student help routes (canonical /api/help-requests* user endpoints)."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.responses import api_response, error_response
from student.help.service import create_request as svc_create, list_requests as svc_list, get_request as svc_get, add_info as svc_add

bp = Blueprint('student_help', __name__)

EXTRA_KEYS = [
    'current_mentor', 'mentor_name', 'reason_change', 'reason_for_change', 'urgency',
    'student_involved', 'student_name', 'mentorship_related', 'incident_category',
    'incident_date', 'supporting_documents', 'supporting_info', 'evidence',
    'confidential', 'mentor_change_reason',
]


def _owns(ticket: dict, u: dict) -> bool:
    return u.get('name') in {ticket.get('name'), ticket.get('user_name')} or u.get('id') == ticket.get('user_id')


@bp.get('')
@login_required
def list_help_requests():
    """List help requests, scoped to the current user for non-admins."""
    items = svc_list(current_user(), category=request.args.get('category') or '', status=request.args.get('status') or '', priority=request.args.get('priority') or '')
    return api_response(items=items, total=len(items))


@bp.post('')
@login_required
def create_help_request():
    """Create a new help / support ticket (student & mentor share this endpoint)."""
    u = current_user()
    data = request.get_json() or {}
    ticket_type = data.get('type') or data.get('ticket_type') or 'Other'
    description = (data.get('description') or '').strip()
    if not description:
        return error_response('Ticket description is required', 400)
    payload = dict(data)
    payload['type'] = ticket_type
    if data.get('urgency_level'):
        payload['urgency'] = data.get('urgency_level')
    _tl = ticket_type.lower()
    if any(k in _tl for k in ('conduct', 'disciplinary', 'misconduct', 'inappropriate')):
        payload['confidential'] = True
    result = svc_create(payload, u)
    return api_response(result, status=201)


@bp.get('/<int:ticket_id>')
@login_required
def get_help_request(ticket_id: int):
    """Fetch a single help request (owner or admin)."""
    u = current_user()
    ticket = svc_get(ticket_id)
    if not ticket:
        return error_response('Ticket not found', 404)
    if u.get('role') != 'admin' and not _owns(ticket, u):
        return error_response('Ticket not found', 404)
    return api_response(ticket)


@bp.post('/<int:ticket_id>/messages')
@login_required
def add_help_message(ticket_id: int):
    """Provide additional information on a ticket."""
    u = current_user()
    data = request.get_json() or {}
    message = (data.get('message') or data.get('content') or '').strip()
    if not message:
        return error_response('Message is required', 400)
    if u.get('role') != 'admin':
        ticket = svc_get(ticket_id)
        if ticket and not _owns(ticket, u):
            return error_response('Ticket not found', 404)
    result = svc_add(ticket_id, u, message)
    if result.get('status') == 404:
        return error_response('Ticket not found', 404)
    return api_response(result)
