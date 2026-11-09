"""Admin help management routes (/api/admin/help-requests*)."""
from __future__ import annotations

from flask import Blueprint, request

from common.middleware.role import roles
from common.responses import api_response, error_response
from common.database.state import get_state
from common.help.admin_management import set_help_status as svc_status, assign_help_request as svc_assign, log_intervention as svc_log

bp = Blueprint('admin_help_management', __name__)


@bp.get('/help-requests')
@roles('admin')
def admin_list_help_requests():
    """List all help requests for the admin support dashboard."""
    items = list(get_state().get('tickets') or [])
    return api_response(items=items, total=len(items))


@bp.patch('/help-requests/<int:ticket_id>/status')
@roles('admin')
def admin_set_help_status(ticket_id: int):
    """Admin: update help request status / decision."""
    data = request.get_json() or {}
    result = svc_status(ticket_id, data.get('status') or 'Under Review', resolution_notes=data.get('resolution_notes') or '', decision=data.get('decision') or '')
    if result.get('error'):
        code = result.get('status', 400) if isinstance(result.get('status'), int) else 400
        return error_response(result.get('error', 'Invalid status'), code)
    return api_response(result)


@bp.post('/help-requests/<int:ticket_id>/assign')
@roles('admin')
def admin_assign_help_request(ticket_id: int):
    """Admin: assign a help request to an administrator."""
    result = svc_assign(ticket_id, (request.get_json() or {}).get('assigned_admin', '').strip())
    if result.get('error'):
        return error_response(result['error'], result.get('status', 404))
    return api_response(result)


@bp.post('/help-requests/<int:ticket_id>/interventions')
@roles('admin')
def admin_add_help_intervention(ticket_id: int):
    """Admin: log an intervention on a help request."""
    data = request.get_json() or {}
    intervention = {'help_request_id': ticket_id, 'action': data.get('action') or 'Note', 'performed_by': (data.get('performed_by') or '').strip(), 'notes': data.get('notes') or '', 'decision': data.get('decision') or '', 'resolution': data.get('resolution') or ''}
    return api_response(svc_log(intervention))
