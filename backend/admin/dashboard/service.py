"""Admin dashboard service (aggregates for IIC dashboard)."""
from __future__ import annotations

from common.database.state import get_state


def admin_dashboard() -> dict:
    """Return aggregate counts for the IIC admin dashboard."""
    state = get_state()
    mentors = state.get('mentors') or []
    reqs = state.get('requests') or []
    students = state.get('students') or []
    tickets = state.get('tickets') or []
    return {
        'students': len(students),
        'mentors': sum(1 for m in mentors if m.get('approved')),
        'pending_approvals': sum(1 for m in mentors if not m.get('approved')),
        'active_mentorships': sum(1 for r in reqs if r.get('status') == 'Accepted'),
        'unmatched_students': sum(1 for x in students if not x.get('mentor')),
        'open_tickets': sum(1 for t in tickets if t.get('status') in ('Submitted', 'Under Review', 'Pending')),
    }
