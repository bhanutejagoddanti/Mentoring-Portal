"""Mentor student-reports service (confidential disciplinary + reassignment intake)."""
from __future__ import annotations

from student.help.service import create_request, list_requests

def report(payload: dict, user: dict) -> dict:
    """Submit a confidential student report (Conduct category)."""
    payload = dict(payload)
    payload['type'] = 'Conduct'
    payload['confidential'] = True
    return create_request(payload, user)

def own_reports(user) -> list:
    """Mentor's own help requests."""
    return list_requests(user)
