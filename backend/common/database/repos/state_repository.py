"""State repository (single responsibility: app_state document persistence)."""
from __future__ import annotations

from datetime import datetime, timezone

from extensions import sb
from common.database.state import default_state


def read_state() -> dict:
    """Read the persisted application state document."""
    result = sb.table('app_state').select('payload').eq('id', 1).limit(1).execute()
    if result.data and result.data[0].get('payload'):
        return result.data[0]['payload']
    payload = default_state()
    sb.table('app_state').upsert({'id': 1, 'payload': payload}).execute()
    return payload


def write_state(payload: dict) -> None:
    """Persist the application state document."""
    sb.table('app_state').upsert({
        'id': 1,
        'payload': payload,
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }).execute()
