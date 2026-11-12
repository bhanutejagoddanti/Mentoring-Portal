"""Shared messaging routes (inbox, direct messages, read receipts, reactions, user search)."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.responses import api_response, error_response
from common.messaging import service as messaging_service

bp = Blueprint('common_messaging', __name__, url_prefix='/api')


@bp.get('/messaging/inbox')
@login_required
def inbox():
    """List DM conversations for the current user (with last message + unread)."""
    user = current_user()
    return api_response(**messaging_service.list_inbox(user))


@bp.post('/messaging/conversations')
@login_required
def create_conversation():
    """Create (or reuse) a direct conversation with another user."""
    user = current_user()
    data = request.get_json(silent=True) or {}
    other_id = (data.get('participant_id') or data.get('user_id') or '').strip()
    if not other_id:
        return error_response('participant_id is required', 400)
    other = messaging_service._user_by_id(other_id)
    if not other:
        return error_response('User not found', 404)
    result = messaging_service.create_direct_conversation(user, other)
    if result.get('error'):
        return error_response(result['error'], result.get('status', 400))
    return api_response({'conversation': result['conversation'], 'created': result.get('created', False)})


@bp.get('/messaging/conversations/<uuid:conversation_id>')
@login_required
def get_conversation(conversation_id: str):
    """Fetch DM conversation detail (participants only)."""
    user = current_user()
    result = messaging_service.get_conversation(conversation_id, user)
    if result.get('error'):
        return error_response(result['error'], result.get('status', 404))
    return api_response(result)


@bp.post('/messaging/conversations/<uuid:conversation_id>/messages')
@login_required
def send_dm(conversation_id: str):
    """Send a direct message in a conversation."""
    user = current_user()
    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()
    attachments = data.get('attachments') or []
    reply_to_id = data.get('reply_to_id') or None
    result = messaging_service.send_message(conversation_id, user, content, reply_to_id, attachments)
    if result.get('error'):
        return error_response(result['error'], result.get('status', 400))
    return api_response(result, status=201)


@bp.post('/messaging/conversations/<uuid:conversation_id>/read')
@login_required
def mark_read(conversation_id: str):
    """Mark conversation messages as read for the current user."""
    user = current_user()
    data = request.get_json(silent=True) or {}
    last_read_message_id = data.get('last_read_message_id') or data.get('message_id') or None
    result = messaging_service.mark_read(conversation_id, user, last_read_message_id=last_read_message_id)
    if result.get('error'):
        return error_response(result['error'], result.get('status', 400))
    return api_response(result)


@bp.post('/messaging/conversations/<uuid:conversation_id>/messages/<uuid:message_id>/reaction')
@login_required
def react_to_message(conversation_id: str, message_id: str):
    """Add/toggle a reaction on a direct message."""
    user = current_user()
    data = request.get_json(silent=True) or {}
    reaction = (data.get('reaction') or '').strip()
    if not reaction:
        return error_response('Reaction is required', 400)
    result = messaging_service.toggle_reaction(conversation_id, message_id, user, reaction)
    if result.get('error'):
        return error_response(result['error'], result.get('status', 400))
    return api_response(result)


@bp.get('/messaging/users')
@login_required
def search_users():
    """Search users (student/mentor/admin) for starting direct conversations."""
    user = current_user()
    query = (request.args.get('q') or '').strip()
    role = request.args.get('role') or None
    try:
        limit = int(request.args.get('limit') or 20)
    except (TypeError, ValueError):
        limit = 20
    items = messaging_service.search_users(query, role, limit)
    return api_response(items=items, total=len(items), query=query)
