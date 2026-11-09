"""Shared community infrastructure routes (discovery, membership, messages, approval workflow)."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.middleware.role import roles
from common.responses import api_response, error_response
from common.database.state import get_state

bp = Blueprint('common_communities', __name__, url_prefix='/api')

# --- discovery -------------------------------------------------------------
@bp.get('/communities')
@login_required
def list_communities():
    """List communities visible to the current user."""
    from common.communities.membership import visible_communities
    return api_response(items=visible_communities(get_state(), current_user()))


@bp.post('/communities')
@roles('admin')
def create_community():
    """Admin-only direct creation."""
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return error_response('Community name is required', 400)
    from common.communities.creation import create_community as svc_create
    u = current_user()
    result = svc_create(u.get('id') or '', u.get('name') or '', data)
    return api_response(result, status=201)


# --- membership ------------------------------------------------------------
@bp.post('/communities/<int:cid>/join')
@login_required
def join_community(cid: int):
    from common.communities.membership import join_community as svc_join
    result = svc_join(cid, current_user())
    if result.get('error'):
        return error_response(result['error'], result.get('status', 404))
    return api_response(result)


@bp.post('/communities/<int:cid>/leave')
@login_required
def leave_community(cid: int):
    from common.communities.membership import leave_community as svc_leave
    result = svc_leave(cid, current_user())
    if result.get('error'):
        return error_response(result['error'], result.get('status', 404))
    return api_response(result)


# --- messages --------------------------------------------------------------
@bp.get('/communities/<int:cid>/messages')
@login_required
def get_community_messages(cid: int):
    from common.communities.messaging import list_messages
    return api_response(items=list_messages(cid))


@bp.post('/communities/<int:cid>/messages')
@login_required
def send_community_message(cid: int):
    from common.communities.messaging import send_message
    data = request.get_json() or {}
    content = (data.get('content') or '').strip()
    if not content:
        return error_response('Message content is required', 400)
    return api_response(send_message(cid, current_user(), content), status=201)


@bp.post('/communities/<int:cid>/report')
@login_required
def report_community_content(cid: int):
    from common.communities.messaging import report_content
    data = request.get_json() or {}
    reason = (data.get('reason') or '').strip()
    if not reason:
        return error_response('Reason for report is required', 400)
    return api_response(report_content(cid, current_user(), reason, data.get('message_id')), status=201)


# --- creation requests (approval workflow owned by admin/community_approvals service) ---
@bp.post('/community-requests')
@login_required
def create_community_request():
    from common.communities.creation import create_community_request as svc_create
    u = current_user()
    data = request.get_json() or {}
    result = svc_create(requester_id=u.get('id') or '', requester_name=u.get('name') or '', requester_role=u.get('role') or 'student', payload=data)
    if result.get('error'):
        return error_response(result['error'], result.get('status', 400) if isinstance(result.get('status'), int) else 400)
    return api_response(result, status=201)


@bp.get('/community-requests')
@login_required
def list_community_requests():
    from common.communities.creation import list_community_requests as svc_list
    items = svc_list(current_user())
    return api_response(items=items, total=len(items))


@bp.get('/community-requests/<int:cid>')
@login_required
def get_community_request(cid: int):
    from common.communities.creation import get_community_request as svc_get
    item = svc_get(cid)
    if not item:
        return error_response('Community request not found', 404)
    return api_response(item)


@bp.post('/community-requests/<int:cid>/approve')
@roles('admin')
def approve_community_request(cid: int):
    from common.communities.approval import approve_request
    data = request.get_json() or {}
    result = approve_request(cid, reviewer_name=current_user().get('name') or '', moderators=data.get('moderators') or data.get('suggested_moderators'))
    if result.get('error'):
        return error_response(result['error'], result.get('status', 404))
    return api_response(result)


@bp.post('/community-requests/<int:cid>/reject')
@roles('admin')
def reject_community_request(cid: int):
    from common.communities.approval import reject_request
    data = request.get_json() or {}
    result = reject_request(cid, reviewer_name=current_user().get('name') or '', reason=data.get('reason') or '')
    if result.get('error'):
        return error_response(result['error'], result.get('status', 404))
    return api_response(result)


@bp.post('/community-requests/<int:cid>/request-changes')
@roles('admin')
def request_community_changes(cid: int):
    from common.communities.approval import request_changes
    data = request.get_json() or {}
    result = request_changes(cid, note=data.get('note') or '')
    if result.get('error'):
        return error_response(result['error'], result.get('status', 404))
    return api_response(result)
