"""Notification repository for the IITM BS Mentoring Portal backend."""
from __future__ import annotations

from extensions import sb


def insert_notification(notification: dict) -> None:
    """Persist a user notification."""
    sb.table('notifications').insert({
        'user_id': notification.get('user_id'),
        'type': notification.get('type', 'info'),
        'title': notification.get('title', ''),
        'body': notification.get('body', ''),
        'read': bool(notification.get('read', False)),
    }).execute()
