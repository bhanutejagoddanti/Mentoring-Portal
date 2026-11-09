"""Student mentorship service (requests, preferences, active tracking)."""
from __future__ import annotations

from datetime import datetime

from common.database.state import get_state, save_state
from common.helpers.constants import DEFAULT_TERM


def create_request(student_name: str, student_email: str, mentor_name: str, goal: str, message: str, term: str, preferences: list | None = None) -> dict:
    """Create a formal mentorship request gated by the term window.

    preferences: optional list of mentor IDs/names the student selected after
    seeing recommendations (persisted for mentor/admin visibility).
    """
    state = get_state()
    if (state.get('term') or DEFAULT_TERM).get('start') and (state.get('term') or DEFAULT_TERM).get('start') > datetime.now().strftime('%Y-%m-%d'):
        return {'error': 'The mentoring request window is not yet open.', 'status': 409}
    if not mentor_name:
        return {'error': 'Mentor is required', 'status': 400}
    request_item = {
        'id': int(datetime.now().timestamp() * 1000), 'student': student_name,
        'email': student_email, 'mentor': mentor_name, 'goal': goal,
        'message': message, 'status': 'Pending', 'term': term,
        'preferences': list(preferences or []),
    }
    state.setdefault('requests', []).append(request_item)
    save_state(state)
    return {'status': 'created', 'request': request_item, 'term': term}


def list_requests() -> list:
    """Return all mentorship requests (routes scope by owner)."""
    return list(get_state().get('requests') or [])


def own_requests(user: dict) -> list:
    """Return this student's requests."""
    return [r for r in list_requests() if r.get('email') == user.get('email') or r.get('student') == user.get('name')]
