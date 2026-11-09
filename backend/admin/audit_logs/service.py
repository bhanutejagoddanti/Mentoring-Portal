"""Audit log service (interventions + decisions trail)."""
from __future__ import annotations
from common.database.state import get_state

def intervention_trail() -> list:
    """Flatten intervention history across tickets."""
    state = get_state()
    out = []
    for t in state.get('tickets') or []:
        for iv in t.get('interventions') or []:
            out.append({'ticket_id': t.get('id'), **iv})
    return out
