"""Community content moderation (reports, actions) - admin only."""
from __future__ import annotations

from extensions import sb
from common.database.state import get_state, save_state


def list_reports(status: str | None = None, limit: int = 100) -> list:
    """List community content reports (newest first)."""
    try:
        res = (
            sb.table('content_reports')
            .select('*')
            .order('created_at', desc=True)
            .limit(limit)
            .execute()
        )
        rows = res.data or []
    except Exception:
        rows = []
    if status:
        rows = [r for r in rows if r.get('status') == status]
    return rows


def set_report_status(report_id: str, status: str, action_note: str = '') -> dict:
    """Update a content report status (Reviewed / Dismissed / Actioned)."""
    sb.table('content_reports').update({'status': status}).eq('id', report_id).execute()
    return {'status': status, 'report_id': report_id, 'action_note': action_note}


def delete_community_message(cid: int, message_id) -> dict:
    """Delete a community message from the working state (moderation action)."""
    state = get_state()
    messages = state.setdefault('community_messages', [])
    before = len(messages)
    filtered = [m for m in messages if not (int(m.get('community_id', -1)) == cid and int(m.get('id', -1)) == int(message_id))]
    state['community_messages'] = filtered
    save_state(state)
    return {'deleted': before - len(filtered), 'status': 'deleted'}
