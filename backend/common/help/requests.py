"""User-facing help requests (student & mentor create/list/read/message)."""
from __future__ import annotations

from common.database.repos.help_repository import insert_help_request, insert_help_message
from common.help.common import find_ticket, is_own, now_iso
from common.database.state import get_state, save_state


def create_help_request(user_id: str, user_name: str, user_email: str, user_role: str, ticket_type: str, description: str, priority: str = 'Medium', extra: dict | None = None) -> dict:
    """Create a new help / support ticket. Source of truth is app_state.tickets."""
    import time
    extra = extra or {}
    ticket = {
        'id': int(time.time() * 1000),
        'user_id': user_id,
        'user_name': user_name,
        'name': user_name,
        'user_email': user_email,
        'role': user_role,
        'type': ticket_type,
        'ticket_type': ticket_type,
        'description': description,
        'status': 'Submitted',
        'priority': priority,
        'reply': '',
        'assigned_admin': '',
        'resolution_notes': '',
        'decision': '',
        'messages': [],
        'interventions': [],
        'created_at': now_iso(),
    }
    for k, v in extra.items():
        if v not in (None, ''):
            ticket[k] = v
    try:
        insert_help_request(ticket)
    except Exception:
        pass
    state = get_state()
    state.setdefault('tickets', []).insert(0, ticket)
    save_state(state)
    return {'status': 'created', 'ticket': ticket}


def list_help_requests(user=None, category: str = '', status: str = '', priority: str = '') -> list:
    """List help requests, scoped to the current user for non-admins, with filters."""
    state = get_state()
    tickets = list(state.get('tickets') or [])
    if user is None or user.get('role') != 'admin':
        tickets = [t for t in tickets if is_own(t, user)]
    if category:
        tickets = [t for t in tickets if (t.get('type') or t.get('ticket_type') or '').lower() == category.lower()]
    if status:
        tickets = [t for t in tickets if (t.get('status') or '').lower() == status.lower()]
    if priority:
        tickets = [t for t in tickets if (t.get('priority') or '').lower() == priority.lower()]
    return tickets


def get_help_request(ticket_id: int):
    """Fetch a single help request by id."""
    state = get_state()
    return find_ticket(state.get('tickets') or [], ticket_id)


def add_help_message(ticket_id: int, sender_id: str, sender_name: str, sender_role: str, message: str, is_internal: bool = False) -> dict:
    """Append a conversation message to a help request (state + best-effort table)."""
    state = get_state()
    ticket = find_ticket(state.get('tickets') or [], ticket_id)
    if not ticket:
        return {'error': 'Ticket not found', 'status': 404}
    msg = {
        'sender_id': sender_id,
        'sender_name': sender_name,
        'sender_role': sender_role,
        'message': message,
        'is_internal': is_internal,
        'created_at': now_iso(),
    }
    ticket.setdefault('messages', []).append(msg)
    if sender_role == 'admin' and not is_internal and message:
        ticket['reply'] = message
        if ticket.get('status') in ('Submitted', 'Additional Information Required'):
            ticket['status'] = 'Under Review'
    save_state(state)
    try:
        insert_help_message({'help_request_id': ticket_id, **msg})
    except Exception:
        pass
    return {'status': 'added', 'message': msg}
