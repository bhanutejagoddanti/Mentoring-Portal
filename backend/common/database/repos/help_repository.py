"""Help repository for the IITM BS Mentoring Portal backend."""
from __future__ import annotations
from extensions import sb

def _safe(fn, label):
    try:
        return fn()
    except Exception as exc:
        try:
            from flask import current_app
            current_app.logger.warning('%s notice: %s', label, exc)
        except Exception:
            pass
        return None

def insert_help_request(ticket: dict) -> None:
    """Persist a new help / support request (best-effort, state is source of truth)."""
    row = {
        'user_id': ticket.get('user_id'),
        'user_name': ticket.get('user_name') or ticket.get('name'),
        'user_email': ticket.get('user_email'),
        'role': ticket.get('role'),
        'ticket_type': ticket.get('ticket_type') or ticket.get('type'),
        'description': ticket.get('description'),
        'status': ticket.get('status', 'Submitted'),
    }
    _safe(lambda: sb.table('help_requests').insert(row).execute(), 'help_requests insert')

def insert_help_message(message: dict) -> None:
    """Persist a help request conversation message (best-effort)."""
    row = {
        'help_request_id': message.get('help_request_id') or message.get('ticket_id') or message.get('id'),
        'sender_id': message.get('sender_id'),
        'sender_name': message.get('sender_name'),
        'sender_role': message.get('sender_role'),
        'message': message.get('message') or message.get('content'),
        'is_internal': bool(message.get('is_internal', False)),
    }
    _safe(lambda: sb.table('help_request_messages').insert(row).execute(), 'help_request_messages insert')

def insert_intervention(intervention: dict) -> None:
    """Persist an admin intervention log entry (best-effort)."""
    _safe(lambda: sb.table('intervention_logs').insert(intervention).execute(), 'intervention_logs insert')
