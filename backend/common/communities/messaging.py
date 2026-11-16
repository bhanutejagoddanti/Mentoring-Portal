"""Community messaging and moderation reports."""
from __future__ import annotations

from common.database.state import get_state, save_state


def list_messages(cid: int) -> list:
    """List community messages for a community (most recent last, capped)."""
    state = get_state()
    items = [m for m in state.get('community_messages') or [] if int(m.get('community_id', -1)) == cid]
    items = items[-100:]
    return items


def send_message(cid: int, user: dict, content: str, reply_to_id=None, attachments: list | None = None) -> dict:
    """Send a community message (members only; admins may moderate without joining)."""
    content = (content or '').strip()
    if not content:
        return {'error': 'Message content is required', 'status': 400}
    state = get_state()
    community = next((c for c in state.get('communities') or [] if int(c.get('id', -1)) == cid), None)
    if not community:
        return {'error': 'Community not found', 'status': 404}
    is_member = any(
        m.get('user_id') == (user.get('id') or '') and m.get('status') == 'active'
        for m in community.get('members') or []
    )
    if not is_member and user.get('role') != 'admin':
        return {'error': 'Join this community before posting messages', 'status': 403}
    import time
    msg = {
        'id': int(time.time() * 1000),
        'community_id': cid,
        'sender_id': user.get('id'),
        'sender_name': user.get('name'),
        'content': content,
        'reply_to_id': reply_to_id,
        'attachments': attachments or [],
        'created_at': new_time_str(),
    }
    state.setdefault('community_messages', []).append(msg)
    save_state(state)
    return msg


def new_time_str() -> str:
    from datetime import datetime
    return datetime.now().strftime('%H:%M')


def set_reaction(cid: int, message_id, user: dict, reaction: str) -> dict:
    """Toggle a reaction on a community message."""
    state = get_state()
    messages = state.setdefault('community_messages', [])
    target = next((m for m in messages if int(m.get('id', -1)) == int(message_id)), None)
    if not target:
        return {'error': 'Message not found', 'status': 404}
    reactions = list(target.get('reactions') or [])
    mine = [r for r in reactions if r.get('user_id') == (user.get('id') or '')]
    has = any(r.get('reaction') == reaction for r in mine)
    if has:
        reactions = [r for r in reactions if not (r.get('user_id') == (user.get('id') or '') and r.get('reaction') == reaction)]
    else:
        reactions.append({'user_id': user.get('id') or '', 'user_name': user.get('name') or '', 'reaction': reaction})
    target['reactions'] = reactions
    save_state(state)
    return {'message_id': message_id, 'reactions': reactions, 'status': 'updated'}


def list_members(cid: int) -> list:
    """List active members of a community."""
    state = get_state()
    community = next((c for c in state.get('communities') or [] if int(c.get('id', -1)) == cid), None)
    if not community:
        return []
    return [m for m in community.get('members') or [] if m.get('status') == 'active']


def report_content(cid: int, user: dict, reason: str, message_id=None) -> dict:
    """Queue a content report for admin moderation.

    Communities and their messages live in the synced app_state (integer ids),
    so reports are stored alongside them. The legacy Supabase `content_reports`
    table uses UUID foreign keys and cannot reference app_state ids.
    """
    import uuid
    from datetime import datetime, timezone

    state = get_state()
    community = next((c for c in state.get('communities') or [] if int(c.get('id', -1)) == cid), None)
    if not community:
        return {'error': 'Community not found', 'status': 404}
    report = {
        'id': str(uuid.uuid4()),
        'reported_by': user.get('id') or '',
        'reporter_name': user.get('name') or '',
        'community_id': cid,
        'community_name': community.get('name') or '',
        'message_id': message_id,
        'reason': reason,
        'status': 'Pending',
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    state.setdefault('content_reports', []).append(report)
    save_state(state)
    return {
        'message': 'Report received and queued for admin moderation.',
        'status': 'queued',
        'report_id': report['id'],
        'report': report,
    }
