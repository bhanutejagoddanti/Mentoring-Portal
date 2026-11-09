"""Student help service (mentor-change + support requests, student perspective)."""
from __future__ import annotations

from common.help.requests import create_help_request as _create, list_help_requests as _list, get_help_request as _get, add_help_message as _add

# Re-export shared implementations (common logic lives in services.help;
# student-specific validation stays here).
def create_request(payload: dict, user: dict) -> dict:
    """Create a student help request with student-specific extra fields."""
    extra = {k: payload.get(k) for k in ['current_mentor', 'reason_change', 'urgency', 'supporting_info'] if payload.get(k)}
    return _create(user_id=user.get('id') or '', user_name=user.get('name') or '', user_email=user.get('email') or '',
                   user_role=user.get('role') or 'student', ticket_type=payload.get('type') or payload.get('ticket_type') or 'Other',
                   description=payload.get('description') or '', priority=payload.get('priority') or 'Medium', extra=extra)

def list_requests(user, **filters):
    return _list(user=user, **filters)

def get_request(ticket_id: int):
    return _get(ticket_id)

def add_info(ticket_id: int, user: dict, message: str):
    return _add(ticket_id=ticket_id, sender_id=user.get('id') or '', sender_name=user.get('name') or '',
                sender_role=user.get('role') or 'student', message=message, is_internal=False)
