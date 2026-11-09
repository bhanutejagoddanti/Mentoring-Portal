"""Community messaging and moderation reports."""
from __future__ import annotations

from common.database.state import get_state, save_state


def list_messages(cid: int) -> list:
    """List community messages."""
    state = get_state()
    return [m for m in state.get('community_messages') or [] if int(m.get('community_id', -1)) == cid][-100:]


def send_message(cid: int, user: dict, content: str) -> dict:
    """Send a community message."""
    import time
    msg = {
        'id': int(time.time() * 1000),
        'community_id': cid,
        'sender_id': user.get('id'),
        'sender_name': user.get('name'),
        'content': content,
        'created_at': '12:00',
    }
    state = get_state()
    state.setdefault('community_messages', []).append(msg)
    save_state(state)
    return msg


def report_content(cid: int, user: dict, reason: str, message_id=None) -> dict:
    """Queue a content report for admin moderation."""
    from extensions import sb

    sb.table('content_reports').insert({
        'reported_by': user.get('id'),
        'community_id': cid,
        'message_id': message_id,
        'reason': reason,
        'status': 'Pending',
    }).execute()
    return {'message': 'Report received and queued for admin moderation.', 'status': 'queued'}
