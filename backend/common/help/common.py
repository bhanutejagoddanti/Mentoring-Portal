"""Shared help-domain helpers (single responsibility: statuses + ownership)."""
from __future__ import annotations

ALLOWED_STATUSES = [
    'Submitted',
    'Under Review',
    'Additional Information Required',
    'Approved',
    'Rejected',
    'Resolved',
    'Closed',
]


def now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def is_own(ticket: dict, user) -> bool:
    if not user:
        return False
    names = {ticket.get('name'), ticket.get('user_name')}
    ids = {ticket.get('user_id')}
    return user.get('name') in names or (user.get('id') in ids if user.get('id') else False)


def find_ticket(tickets: list, ticket_id: int):
    return next((t for t in tickets or [] if int(t.get('id', -1)) == int(ticket_id)), None)
