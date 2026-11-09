"""Disciplinary report review service (confidential; admin-only decisions)."""
from __future__ import annotations
from common.help.admin_management import set_help_status, log_intervention
from common.help.requests import list_help_requests

def list_disciplinary(user=None) -> list:
    """List confidential conduct reports."""
    return [t for t in list_help_requests(user=user) if t.get('confidential') or 'conduct' in str(t.get('type','')).lower()]

__all__ = ['list_disciplinary', 'set_help_status', 'log_intervention']
