"""Shared notification routes."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.responses import api_response, error_response
from extensions import sb

bp = Blueprint('common_notifications', __name__, url_prefix='/api/notifications')


@bp.get('')
@login_required
def list_notifications():
    """List notifications for the current user."""
    u = current_user()
    items = (
        sb.table('notifications')
        .select('*')
        .eq('user_id', u.get('id'))
        .order('created_at', desc=True)
        .limit(50)
        .execute()
        .data
    )
    return api_response(items=items or [], total=len(items or []))


@bp.post('')
@login_required
def create_notification_route():
    """Create a notification for the current user."""
    from common.notifications.service import create_notification
    u = current_user()
    data = request.get_json() or {}
    result = create_notification(user_id=u.get('id') or '', notification_type=data.get('type') or 'info', title=data.get('title') or '', body=data.get('body') or '', link=data.get('link') or '')
    return api_response(result, status=201)


@bp.post('/read-all')
@login_required
def mark_all_read():
    """Mark all notifications for the current user as read."""
    from common.notifications.service import mark_all_read
    u = current_user()
    updated = mark_all_read(u.get('id') or '')
    return api_response({'updated': updated})


@bp.post('/<uuid:notification_id>/read')
@login_required
def mark_read(notification_id: str):
    """Mark a single notification as read (owner only)."""
    from common.notifications.service import mark_read
    u = current_user()
    item = mark_read(notification_id, u.get('id') or '')
    if not item:
        return error_response('Notification not found', 404)
    return api_response(item)


@bp.get('/unread-count')
@login_required
def unread_count():
    """Return unread notification count for the current user."""
    from common.notifications.service import unread_count
    u = current_user()
    return api_response({'count': unread_count(u.get('id') or '')})
