"""Community membership (join / leave and visibility)."""
from __future__ import annotations

from common.database.state import get_state, save_state


def visible_communities(state: dict, user: dict) -> list:
    """Return communities visible to the current user."""
    result = []
    for c in state.get('communities') or []:
        members = c.setdefault('members', [])
        joined = any(x.get('user_id') == user.get('id') and x.get('status') == 'active' for x in members)
        if c.get('visibility', 'public') == 'public' or joined or user.get('role') == 'admin':
            result.append({
                'id': c.get('id'),
                'name': c.get('name'),
                'description': c.get('description', ''),
                'category': c.get('category', 'General'),
                'visibility': c.get('visibility', 'public'),
                'joined': joined,
                'member_count': sum(1 for x in members if x.get('status') == 'active') or c.get('member_count', 1),
            })
    return result


def join_community(cid: int, user: dict) -> dict:
    """Join a community."""
    state = get_state()
    c = next((x for x in state.get('communities') or [] if int(x.get('id', -1)) == cid), None)
    if not c:
        return {'error': 'Community not found', 'status': 404}
    members = c.setdefault('members', [])
    existing = next((x for x in members if x.get('user_id') == user.get('id')), None)
    if existing:
        existing['status'] = 'active'
    else:
        status = 'active' if c.get('visibility') == 'public' or user.get('role') == 'admin' else 'pending'
        members.append({'user_id': user.get('id'), 'name': user.get('name'), 'role': 'member', 'status': status})
    c['member_count'] = sum(1 for x in members if x.get('status') == 'active')
    save_state(state)
    return {'message': 'Joined community', 'status': 'active'}


def leave_community(cid: int, user: dict) -> dict:
    """Leave a community."""
    state = get_state()
    c = next((x for x in state.get('communities') or [] if int(x.get('id', -1)) == cid), None)
    if not c:
        return {'error': 'Community not found', 'status': 404}
    c['members'] = [x for x in c.get('members') or [] if x.get('user_id') != user.get('id')]
    c['member_count'] = max(0, sum(1 for x in c.get('members') or [] if x.get('status') == 'active'))
    save_state(state)
    return {'message': 'Left community'}
