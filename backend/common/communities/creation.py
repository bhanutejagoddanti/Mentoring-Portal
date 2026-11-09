"""Community creation (single responsibility: direct create + request intake)."""
from __future__ import annotations

from extensions import sb
from common.database.repos.community_repository import insert_community_request
from common.database.state import get_state, save_state


def create_community(creator_id: str, creator_name: str, payload: dict) -> dict:
    """Create an approved community directly (admin / system flow)."""
    state = get_state()
    cid = max([int(c.get('id', 0)) for c in state.get('communities') or []] + [0]) + 1
    comm = {
        'id': cid,
        'name': (payload.get('name') or '').strip(),
        'description': payload.get('description') or '',
        'category': payload.get('category') or 'General',
        'visibility': payload.get('visibility') or 'public',
        'creator_id': creator_id,
        'member_count': 1,
        'members': [{'user_id': creator_id, 'name': creator_name, 'role': 'owner', 'status': 'active'}],
    }
    try:
        sb.table('communities').insert({
            'name': comm['name'],
            'description': comm['description'],
            'category': comm['category'],
            'visibility': comm['visibility'],
            'creator_id': creator_id,
        }).execute()
    except Exception as exc:
        try:
            from flask import current_app
            current_app.logger.warning('communities insert notice: %s', exc)
        except Exception:
            pass
    state.setdefault('communities', []).append(comm)
    save_state(state)
    return {'status': 'created', 'community': comm}


def create_community_request(requester_id: str, requester_name: str, requester_role: str, payload: dict) -> dict:
    """Create a pending community creation request (state is source of truth)."""
    import time
    request_payload = {
        'id': int(time.time() * 1000),
        'requester_id': requester_id,
        'requester_name': requester_name,
        'requester_role': requester_role,
        'community_name': (payload.get('community_name') or (payload.get('name') or '')).strip(),
        'description': payload.get('description') or '',
        'category': payload.get('category') or 'General',
        'purpose': payload.get('purpose') or '',
        'target_audience': payload.get('target_audience') or '',
        'community_type': payload.get('community_type') or 'Discussion',
        'reason': payload.get('reason') or '',
        'suggested_moderators': payload.get('suggested_moderators') or payload.get('moderators') or [],
        'supporting_info': payload.get('supporting_info') or '',
        'status': 'Pending',
        'reviewed_by': '',
        'reviewed_at': None,
        'rejection_reason': '',
        'moderation_note': '',
        'created_community_id': None,
    }
    if not request_payload['community_name']:
        return {'error': 'Community name is required', 'status': 400}
    try:
        insert_community_request(request_payload)
    except Exception:
        pass
    state = get_state()
    state.setdefault('community_requests', []).insert(0, request_payload)
    save_state(state)
    return {'status': 'pending', 'request': request_payload}


def list_community_requests(user) -> list:
    """List community requests (admin: all, others: own)."""
    state = get_state()
    items = list(state.get('community_requests') or [])
    if not user or user.get('role') != 'admin':
        items = [x for x in items if x.get('requester_id') == (user or {}).get('id') or x.get('requester_name') == (user or {}).get('name')]
    return items


def get_community_request(cid: int) -> dict | None:
    """Fetch a single community creation request."""
    state = get_state()
    return next((x for x in state.get('community_requests') or [] if int(x.get('id', -1)) == cid), None)
