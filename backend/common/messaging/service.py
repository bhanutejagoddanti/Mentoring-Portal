"""Shared messaging service (conversations, DMs, read receipts, reactions, user search)."""
from __future__ import annotations

from common.database.repos import messaging_repository as repo
from common.notifications.service import create_notification


def _other_participant(conversation_id: str, user_id: str) -> dict | None:
    from extensions import sb
    rows = (
        sb.table('conversation_participants')
        .select('conversation_id, user_id, role, status, last_read_at, unread_count, joined_at')
        .eq('conversation_id', conversation_id)
        .eq('status', 'active')
        .execute()
        .data
        or []
    )
    for row in rows:
        if row.get('user_id') != user_id:
            return row
    return None


def _messages_for(conversation_id: str) -> list:
    return repo.list_messages(conversation_id)


def _unread_for(user_id: str, last_read_at: str | None, messages: list) -> int:
    if not last_read_at:
        return len([m for m in messages if m.get('sender_id') != user_id])
    from datetime import datetime
    try:
        lr = datetime.fromisoformat(str(last_read_at).replace('Z', '+00:00'))
    except Exception:
        lr = None
    if lr is None:
        return len([m for m in messages if m.get('sender_id') != user_id])
    return len([
        m for m in messages
        if m.get('sender_id') != user_id and datetime.fromisoformat(str(m.get('created_at')).replace('Z', '+00:00')) > lr
    ])


def list_inbox(user: dict) -> dict:
    """Return DM conversations for the current user with last message + unread counts."""
    items = []
    user_id = user.get('id') or ''
    for row in repo.list_user_conversations(user_id):
        conv = row.get('conversations') or {}
        cid = row.get('conversation_id')
        messages = _messages_for(cid)
        last = messages[-1] if messages else None
        unread = _unread_for(user_id, row.get('last_read_at'), messages)
        other = _other_participant(cid, user_id)
        peer_user = _user_by_id(other.get('user_id') or '') if other else None
        items.append({
            'conversation_id': cid,
            'type': conv.get('type') or 'direct',
            'community_id': conv.get('community_id'),
            'status': conv.get('status') or 'active',
            'created_at': conv.get('created_at'),
            'updated_at': conv.get('updated_at') or (last or {}).get('created_at'),
            'last_message_at': conv.get('last_message_at') or (last or {}).get('created_at'),
            'last_message': last,
            'unread_count': unread,
            'member_role': row.get('role') or 'member',
            'other': {
                'user_id': other.get('user_id') if other else '',
                'name': peer_user.get('name') if peer_user else '',
                'email': peer_user.get('email') if peer_user else '',
                'role': other.get('role') or 'member',
                'status': other.get('status') or 'active',
                'last_read_at': other.get('last_read_at'),
            } if other else None,
        })
    return {'items': items, 'total': len(items)}


def _participant_public(p: dict) -> dict:
    return {
        'user_id': p.get('user_id') or '',
        'name': '',
        'role': p.get('role') or 'member',
        'status': p.get('status') or 'active',
        'last_read_at': p.get('last_read_at'),
    }


def create_direct_conversation(user: dict, other_user: dict) -> dict:
    """Find existing DM between two users or create a new one."""
    user_id = user.get('id') or ''
    other_id = other_user.get('id') or ''
    if not user_id or not other_id:
        return {'error': 'Invalid conversation participants', 'status': 400}
    existing = repo.find_direct_conversation(user_id, other_id)
    if existing and existing.get('id'):
        return {'conversation': existing, 'created': False}
    created_by = user_id if (user.get('approved', True) or user.get('role') == 'admin') else other_id
    conversation = repo.create_direct_conversation(user_id, other_id, created_by)
    if not conversation or not conversation.get('id'):
        return {'error': 'Failed to create conversation', 'status': 500}
    return {'conversation': {'id': conversation['id']}, 'created': True}


def get_conversation(conversation_id: str, user: dict) -> dict | None:
    """Fetch conversation detail for a participant."""
    conv = repo.get_conversation(conversation_id)
    if not conv:
        return {'error': 'Conversation not found', 'status': 404}
    participant = None
    from extensions import sb
    rows = (
        sb.table('conversation_participants')
        .select('*')
        .eq('conversation_id', conversation_id)
        .eq('user_id', user.get('id') or '')
        .eq('status', 'active')
        .limit(1)
        .execute()
        .data
        or []
    )
    participant = rows[0] if rows else None
    if not participant:
        return {'error': 'Conversation not found', 'status': 404}
    messages = _messages_for(conversation_id)
    unread = _unread_for(user.get('id') or '', participant.get('last_read_at'), messages)
    peer = _other_participant(conversation_id, user.get('id') or '')
    peer_user = _user_by_id(peer.get('user_id') or '') if peer else None
    return {
        'conversation': conv,
        'participant': participant,
        'messages': messages,
        'unread_count': unread,
        'other': {
            'user_id': peer.get('user_id') if peer else '',
            'name': peer_user.get('name') if peer_user else '',
            'email': peer_user.get('email') if peer_user else '',
            'role': peer.get('role') or 'member',
            'status': peer.get('status') or 'active',
            'last_read_at': peer.get('last_read_at'),
        } if peer else None,
    }


def send_message(conversation_id: str, user: dict, content: str, reply_to_id: str | None = None, attachments: list | None = None) -> dict:
    """Send a direct message (participant-authorized) and notify the peer."""
    content = (content or '').strip()
    if not content:
        return {'error': 'Message content is required', 'status': 400}
    if attachments is not None:
        if not isinstance(attachments, list):
            return {'error': 'Attachments must be a list', 'status': 400}
        for att in attachments:
            if not isinstance(att, dict) or not (att.get('name') or '').strip():
                return {'error': 'Each attachment needs a name', 'status': 400}
            try:
                if att.get('size') and int(att.get('size')) > 5 * 1024 * 1024:
                    return {'error': 'Attachment too large (max 5MB)', 'status': 400}
            except (TypeError, ValueError):
                return {'error': 'Invalid attachment size', 'status': 400}
    conv = repo.get_conversation(conversation_id)
    if not conv:
        return {'error': 'Conversation not found', 'status': 404}
    from extensions import sb
    rows = (
        sb.table('conversation_participants')
        .select('*')
        .eq('conversation_id', conversation_id)
        .eq('user_id', user.get('id') or '')
        .eq('status', 'active')
        .limit(1)
        .execute()
        .data
        or []
    )
    if not rows:
        return {'error': 'Conversation not found', 'status': 404}
    message = repo.insert_message(conversation_id, user.get('id') or '', user.get('name') or '', user.get('role') or 'student', content, reply_to_id, attachments)
    peer = _other_participant(conversation_id, user.get('id') or '')
    if peer:
        other_user = _user_by_id(peer.get('user_id') or '')
        if other_user:
            create_notification(
                user_id=other_user.get('id') or '',
                notification_type='message',
                title=f'New message from {user.get("name") or ""}',
                body=content[:200],
                link='/inbox',
            )
    return {'message': message}


def _user_by_id(user_id: str) -> dict:
    from extensions import sb
    rows = sb.table('user_profiles').select('id, name, email, role, approved, active').eq('id', user_id).limit(1).execute().data or []
    return rows[0] if rows else None


def mark_read(conversation_id: str, user: dict, last_read_message_id: str | None = None) -> dict:
    """Mark conversation messages as read for current user."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    messages = repo.list_messages(conversation_id)
    last_msg = messages[-1] if messages else None
    target_message_id = last_read_message_id or (last_msg or {}).get('id')
    unread = 0
    if target_message_id:
        unread = len([m for m in messages if m.get('id') != target_message_id and m.get('sender_id') != (user.get('id') or '')])
    return repo.mark_participant_read(conversation_id, user.get('id') or '', target_message_id, unread)


def toggle_reaction(conversation_id: str, message_id: str, user: dict, reaction: str) -> dict:
    """Toggle/add a reaction on a direct message."""
    conv = repo.get_conversation(conversation_id)
    if not conv:
        return {'error': 'Conversation not found', 'status': 404}
    messages = repo.list_messages(conversation_id)
    message = next((m for m in messages if m.get('id') == message_id), None)
    if not message:
        return {'error': 'Message not found', 'status': 404}
    reactions = list(message.get('reactions') or [])
    mine = [r for r in reactions if r.get('user_id') == (user.get('id') or '')]
    has = any(r.get('reaction') == reaction for r in mine)
    if has:
        reactions = [r for r in reactions if not (r.get('user_id') == (user.get('id') or '') and r.get('reaction') == reaction)]
    else:
        reactions = reactions + [{'user_id': user.get('id') or '', 'user_name': user.get('name') or '', 'reaction': reaction}]
    return repo.set_message_reactions(conversation_id, message_id, reactions)


def search_users(query: str, role: str | None = None, limit: int = 20) -> list:
    """Search users by name/email for starting direct conversations."""
    q = (query or '').strip()
    return repo.search_users(q, role, limit)
