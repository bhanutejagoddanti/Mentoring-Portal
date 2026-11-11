"""Admin community content moderation routes."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.middleware.role import roles
from common.responses import api_response, error_response

bp = Blueprint('admin_community_moderation', __name__, url_prefix='/community-moderation')


@bp.get('/reports')
@roles('admin')
@login_required
def list_community_reports():
    """List community content reports for moderation."""
    status = request.args.get('status') or None
    from admin.community_moderation.service import list_reports
    items = list_reports(status=status)
    return api_response(items=items, total=len(items), status=status)


@bp.post('/reports/<uuid:report_id>/status')
@roles('admin')
@login_required
def set_community_report_status(report_id: str):
    """Update a community content report decision (Reviewed / Dismissed / Actioned)."""
    from admin.community_moderation.service import set_report_status
    data = request.get_json(silent=True) or {}
    status = (data.get('status') or 'Reviewed').strip()
    action_note = (data.get('action_note') or '') or ''
    result = set_report_status(report_id, status, action_note)
    return api_response(result)


@bp.post('/messages/<int:message_id>/delete')
@roles('admin')
@login_required
def delete_community_message(message_id: int):
    """Delete a community message (moderation action)."""
    from admin.community_moderation.service import delete_community_message
    data = request.get_json(silent=True) or {}
    cid = int(data.get('community_id') or 0)
    if not cid:
        return error_response('community_id is required', 400)
    result = delete_community_message(cid, message_id)
    if result.get('deleted') is None:
        return error_response('Message not found', 404)
    return api_response(result)
