"""Taxonomy service (fields/industries/modes option lists)."""
from __future__ import annotations

from common.database.state import get_state


def list_filter_options() -> dict:
    """Distinct taxonomy options."""
    mentors = [m for m in get_state().get('mentors', []) if m.get('approved') and m.get('active', True)]
    return {
        'fields': sorted({m.get('field', '') for m in mentors if m.get('field')}),
        'industries': sorted({m.get('industry', '') for m in mentors if m.get('industry')}),
        'modes': sorted({m.get('mode', '') for m in mentors if m.get('mode')}),
    }
