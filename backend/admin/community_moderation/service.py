"""Community content moderation (reports, actions) - admin only."""
from __future__ import annotations

from datetime import datetime, timezone

from extensions import sb
from common.database.state import get_state, save_state


def list_reports(status: str | None = None, limit: int = 100) -> list:
    """List community content reports (newest first).

    Reports created by the SPA are stored in app_state (integer community ids);
    legacy rows may still live in the Supabase table, so both are merged.
    """
    rows = list(get_state().get('content_reports') or [])
    try:
        legacy = (
            sb.table('content_reports')
            .select('*')
            .order('created_at', desc=True)
            .limit(limit)
            .execute()
            .data
            or []
        )
    except Exception:
        legacy = []
    rows.extend(legacy)
    rows.sort(key=lambda r: str(r.get('created_at') or ''), reverse=True)
    if status:
        rows = [r for r in rows if r.get('status') == status]
    return rows[:limit]


def set_report_status(report_id: str, status: str, action_note: str = '') -> dict:
    """Update a content report status (Reviewed / Dismissed / Actioned)."""
    target = str(report_id)
    state = get_state()
    updated = None
    for report in state.get('content_reports') or []:
        if str(report.get('id')) == target:
            report['status'] = status
            report['action_note'] = action_note
            report['updated_at'] = datetime.now(timezone.utc).isoformat()
            updated = report
            break
    if updated is not None:
        save_state(state)
    else:
        sb.table('content_reports').update({'status': status}).eq('id', target).execute()
    return {'status': status, 'report_id': target, 'action_note': action_note}


def delete_community_message(cid: int, message_id) -> dict:
    """Delete a community message from the working state (moderation action)."""
    state = get_state()
    messages = state.setdefault('community_messages', [])
    before = len(messages)
    filtered = [m for m in messages if not (int(m.get('community_id', -1)) == cid and int(m.get('id', -1)) == int(message_id))]
    state['community_messages'] = filtered
    save_state(state)
    return {'deleted': before - len(filtered), 'status': 'deleted'}
