"""Messaging repository (conversations, participants, DMs, read receipts)."""
from __future__ import annotations

from extensions import sb


def list_user_conversations(user_id: str) -> list:
    """Return the active conversations the user participates in (with metadata)."""
    res = sb.table('conversation_participants')
    res = res.select(
        'conversation_id, user_id, role, status, last_read_at, unread_count, joined_at, '
        'conversations!inner(id, type, community_id, created_by, status, created_at, updated_at, last_message_at)'
    )
    res = res.eq('user_id', user_id)
    res = res.eq('status', 'active')
    res = res.order('joined_at', desc=True)
    return res.execute().data or []


def get_conversation(conversation_id: str) -> dict | None:
    """Fetch a single conversation by id."""
    res = sb.table('conversations').select('*').eq('id', conversation_id).limit(1).execute()
    rows = res.data or []
    return rows[0] if rows else None


def find_direct_conversation(user_id: str, other_user_id: str) -> dict | None:
    """Find an existing active direct conversation between two users."""
    convos = list_user_conversations(user_id)
    for row in convos:
        conv = row.get('conversations') or {}
        if conv.get('type') != 'direct':
            continue
        cid = row.get('conversation_id')
        res = (
            sb.table('conversation_participants')
            .select('user_id, status')
            .eq('conversation_id', cid)
            .execute()
        )
        participants = res.data or []
        if any(p.get('user_id') == other_user_id and p.get('status') == 'active' for p in participants):
            return conv
    return None


def create_direct_conversation(user_a_id: str, user_b_id: str, created_by_id: str) -> dict:
    """Create a new direct conversation between two users."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    conv_res = (
        sb.table('conversations')
        .insert({'type': 'direct', 'status': 'active', 'created_by': created_by_id, 'last_message_at': None})
        .execute()
    )
    conversation_id = (conv_res.data or [{}])[0].get('id')
    if not conversation_id:
        return None
    for uid in (user_a_id, user_b_id):
        sb.table('conversation_participants').insert({
            'conversation_id': conversation_id,
            'user_id': uid,
            'role': 'member',
            'status': 'active',
            'last_read_at': now,
            'unread_count': 0,
        }).execute()
    sb.table('conversation_participants').update({'last_read_at': now}).eq('conversation_id', conversation_id).eq('user_id', user_a_id).execute()
    return {'id': conversation_id}


def insert_participant(conversation_id: str, user_id: str, role: str = 'member') -> dict:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    res = (
        sb.table('conversation_participants')
        .insert({'conversation_id': conversation_id, 'user_id': user_id, 'role': role, 'status': 'active', 'last_read_at': now, 'unread_count': 0})
        .execute()
    )
    return res.data or [{}]


def mark_participant_read(conversation_id: str, user_id: str, last_read_message_id: str | None, unread_count: int = 0) -> dict:
    """Mark messages as read for a participant."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    sb.table('message_reads').upsert({
        'conversation_id': conversation_id,
        'user_id': user_id,
        'last_read_message_id': last_read_message_id,
        'last_read_at': now,
        'updated_at': now,
    }, on_conflict='conversation_id,user_id').execute()
    sb.table('conversation_participants').update({
        'last_read_at': now,
        'unread_count': unread_count,
    }).eq('conversation_id', conversation_id).eq('user_id', user_id).execute()
    return {'conversation_id': conversation_id, 'user_id': user_id, 'unread_count': unread_count}


def list_messages(conversation_id: str) -> list:
    """Return messages of a conversation in chronological order."""
    res = sb.table('direct_messages')
    res = res.select('*')
    res = res.eq('conversation_id', conversation_id)
    res = res.order('created_at', desc=False)
    return res.execute().data or []


def insert_message(conversation_id: str, sender_id: str, sender_name: str, sender_role: str, content: str, reply_to_id: str | None = None, attachments: list | None = None) -> dict:
    """Insert a direct message and bump conversation activity timestamps."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    res = (
        sb.table('direct_messages')
        .insert({
            'conversation_id': conversation_id,
            'sender_id': sender_id,
            'sender_name': sender_name,
            'sender_role': sender_role,
            'content': content,
            'reply_to_id': reply_to_id,
            'attachments': attachments or [],
        })
        .execute()
    )
    sb.table('conversations').update({'updated_at': now, 'last_message_at': now}).eq('id', conversation_id).execute()
    return (res.data or [{}])[0] if res.data else {}


def set_message_reactions(conversation_id: str, message_id: str, reactions: list) -> dict:
    """Replace the reaction set on a direct message."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    res = (
        sb.table('direct_messages')
        .update({'reactions': reactions, 'updated_at': now})
        .eq('id', message_id)
        .eq('conversation_id', conversation_id)
        .execute()
    )
    return (res.data or [{}])[0] if res.data else {}


def search_users(query: str, role: str | None = None, limit: int = 20, exclude_id: str | None = None) -> list:
    """Search user profiles by name/email for starting direct conversations."""
    res = sb.table('user_profiles')
    res = res.select('id, name, email, role, approved, active, avatar_url')
    if query:
        res = res.or_(f"name.ilike.%{query}%,email.ilike.%{query}%")
    if role:
        res = res.eq('role', role)
    res = res.eq('active', True)
    if exclude_id:
        res = res.neq('id', exclude_id)
    res = res.order('name', desc=False)
    res = res.limit(limit)
    return res.execute().data or []
