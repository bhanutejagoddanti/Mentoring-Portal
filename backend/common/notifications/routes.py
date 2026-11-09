"""Shared notification routes."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.responses import api_response
from extensions import sb

bp = Blueprint('common_notifications', __name__, url_prefix='/api/notifications')


@bp.get('')
@login_required
def list_notifications():
    """List notifications for the current user."""
    u = current_user()
    try:
        items = sb.table('notifications').select('*').eq('user_id', u.get('id')).order('created_at', desc=True).limit(50).execute().data
    except Exception:
        items = []
    return api_response(items=items, total=len(items))


@bp.post('')
@login_required
def create_notification_route():
    """Create a notification for the current user."""
    from common.notifications.service import create_notification
    u = current_user()
    data = request.get_json() or {}
    result = create_notification(user_id=u.get('id') or '', notification_type=data.get('type') or 'info', title=data.get('title') or '', body=data.get('body') or '')
    return api_response(result, status=201)
