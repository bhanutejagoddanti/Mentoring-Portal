"""Admin help management (status decisions + intervention audit trail)."""
from __future__ import annotations

from common.database.repos.help_repository import insert_intervention
from common.help.common import ALLOWED_STATUSES, find_ticket, now_iso
from common.database.state import get_state, save_state


def set_help_status(ticket_id: int, status: str, resolution_notes: str = '', decision: str = '') -> dict:
    """Update the status / decision of a help request."""
    if status not in ALLOWED_STATUSES:
        return {'error': f'Invalid status. Allowed: {", ".join(ALLOWED_STATUSES)}', 'status': 400}
    state = get_state()
    ticket = find_ticket(state.get('tickets') or [], ticket_id)
    if not ticket:
        return {'error': 'Ticket not found', 'status': 404}
    ticket['status'] = status
    if decision:
        ticket['decision'] = decision
    if resolution_notes:
        ticket['resolution_notes'] = resolution_notes
    if status == 'Resolved':
        ticket['reply'] = resolution_notes or ticket.get('reply') or ''
    save_state(state)
    return {'status': 'updated', 'ticket': ticket}


def assign_help_request(ticket_id: int, assigned_admin: str) -> dict:
    """Assign a help request to an administrator."""
    state = get_state()
    ticket = find_ticket(state.get('tickets') or [], ticket_id)
    if not ticket:
        return {'error': 'Ticket not found', 'status': 404}
    ticket['assigned_admin'] = assigned_admin
    save_state(state)
    return {'status': 'assigned', 'ticket': ticket}


def log_intervention(intervention: dict) -> dict:
    """Log an admin intervention (state + best-effort table)."""
    state = get_state()
    intervention = dict(intervention)
    intervention.setdefault('performed_at', now_iso())
    intervention.setdefault('performed_by', '')
    ticket_id = intervention.get('help_request_id')
    if ticket_id is not None:
        ticket = find_ticket(state.get('tickets') or [], ticket_id)
        if ticket is not None:
            ticket.setdefault('interventions', []).append(intervention)
    save_state(state)
    try:
        insert_intervention(intervention)
    except Exception:
        pass
    return {'status': 'logged', 'intervention': intervention}
