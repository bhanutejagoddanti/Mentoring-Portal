"""Community approval workflow (admin decisions)."""
from __future__ import annotations

from datetime import datetime, timezone

from common.database.repos.community_repository import insert_community_review
from common.database.state import get_state, save_state


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def approve_request(cid: int, reviewer_name: str = '', moderators=None) -> dict:
    """Approve a community creation request and activate the community."""
    state = get_state()
    req = next((x for x in state.get('community_requests') or [] if int(x.get('id', -1)) == cid), None)
    if not req:
        return {'error': 'Community request not found', 'status': 404}
    communities = state.setdefault('communities', [])
    new_cid = max([int(c.get('id', 0)) for c in communities] + [0]) + 1
    communities.append({
        'id': new_cid,
        'name': req.get('community_name'),
        'description': req.get('description') or '',
        'category': req.get('category') or 'General',
        'visibility': 'public',
        'creator_id': req.get('requester_id'),
        'member_count': 1,
        'members': [{'user_id': req.get('requester_id'), 'name': req.get('requester_name'), 'role': 'owner', 'status': 'active'}],
    })
    req['status'] = 'Approved'
    req['reviewed_by'] = reviewer_name or ''
    req['reviewed_at'] = _now()
    req['created_community_id'] = new_cid
    if moderators:
        req['suggested_moderators'] = moderators
    save_state(state)
    return {'message': 'Community approved and activated.', 'community': communities[-1]}


def reject_request(cid: int, reviewer_name: str = '', reason: str = '') -> dict:
    """Reject a community creation request with a reason."""
    state = get_state()
    req = next((x for x in state.get('community_requests') or [] if int(x.get('id', -1)) == cid), None)
    if not req:
        return {'error': 'Community request not found', 'status': 404}
    decision = {
        'community_request_id': cid,
        'decision': 'Rejected',
        'reason': reason or 'Does not meet IIC guidelines.',
        'reviewed_by': reviewer_name,
        'reviewed_at': _now(),
        'created_community_id': None,
    }
    insert_community_review(decision)
    req['status'] = 'Rejected'
    req['rejection_reason'] = decision['reason']
    req['reviewed_by'] = decision['reviewed_by']
    req['reviewed_at'] = decision['reviewed_at']
    save_state(state)
    return {'message': 'Community request rejected.', 'request': req}


def request_changes(cid: int, note: str = '') -> dict:
    """Request modifications to a pending community creation request."""
    state = get_state()
    req = next((x for x in state.get('community_requests') or [] if int(x.get('id', -1)) == cid), None)
    if not req:
        return {'error': 'Community request not found', 'status': 404}
    req['status'] = 'Pending'
    req['moderation_note'] = note or 'Requested changes.'
    save_state(state)
    return {'message': 'Modification requested for community.', 'request': req}
