"""Shared notification creation + inbox read-state (single responsibility: inbox)."""
from __future__ import annotations

from extensions import sb


def create_notification(user_id: str, notification_type: str, title: str, body: str, link: str = '') -> dict:
    """Create a user notification."""
    try:
        sb.table('notifications').insert({
            'user_id': user_id,
            'type': notification_type,
            'title': title,
            'message': body,
            'read': False,
            'link': link or '',
        }).execute()
    except Exception:
        pass
    return {'status': 'created'}


def list_for_user(user_id: str, limit: int = 50) -> list:
    """List notifications for a user (most recent first)."""
    try:
        return (
            sb.table('notifications')
            .select('*')
            .eq('user_id', user_id)
            .order('created_at', desc=True)
            .limit(limit)
            .execute()
            .data
            or []
        )
    except Exception:
        return []


def mark_read(notification_id: str, user_id: str) -> dict | None:
    """Mark a single notification as read (owner only)."""
    res = (
        sb.table('notifications')
        .update({'read': True})
        .eq('id', notification_id)
        .eq('user_id', user_id)
        .execute()
    )
    rows = res.data or []
    return rows[0] if rows else None


def mark_all_read(user_id: str) -> int:
    """Mark all notifications for a user as read. Returns affected rows."""
    res = (
        sb.table('notifications')
        .update({'read': True})
        .eq('user_id', user_id)
        .eq('read', False)
        .execute()
    )
    try:
        return len(res.data or [])
    except Exception:
        return 0


def unread_count(user_id: str) -> int:
    """Count unread notifications for a user."""
    try:
        rows = (
            sb.table('notifications')
            .select('id')
            .eq('user_id', user_id)
            .eq('read', False)
            .execute()
            .data
            or []
        )
        return len(rows)
    except Exception:
        return 0
