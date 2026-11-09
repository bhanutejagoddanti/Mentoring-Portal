"""Shared notification creation (single responsibility: inbox insert)."""
from __future__ import annotations

from extensions import sb


def create_notification(user_id: str, notification_type: str, title: str, body: str) -> dict:
    """Create a user notification."""
    try:
        sb.table('notifications').insert({'user_id': user_id, 'type': notification_type, 'title': title, 'body': body, 'read': False}).execute()
    except Exception:
        pass
    return {'status': 'created'}
