"""Shared app_state persistence (single source of truth for SPA sync)."""
from __future__ import annotations

from datetime import datetime, timezone

from flask import current_app

from common.helpers.constants import DEFAULT_TERM


def default_state() -> dict:
    """Return the fallback application state used when Supabase is unavailable."""
    return {
        'mentors': [
            {'id': 1, 'name': 'Arjun Nair', 'title': 'Product Analyst', 'field': 'Data & Product', 'industry': 'Finance', 'role': 'Product Analyst', 'mode': 'Online', 'slots': 2, 'bio': 'Product analytics and data strategy.', 'background': 'Product analytics at a fintech company.', 'linkedin': 'https://linkedin.com', 'approved': True, 'active': True},
            {'id': 2, 'name': 'Kavya Iyer', 'title': 'Software Engineer', 'field': 'IT', 'industry': 'Technology', 'role': 'Engineer', 'mode': 'Online', 'slots': 1, 'bio': 'Software engineering and cloud systems.', 'background': 'Builds cloud services for a technology company.', 'linkedin': '', 'approved': True, 'active': True},
            {'id': 3, 'name': 'Meera Shah', 'title': 'Research Scientist', 'field': 'ML', 'industry': 'Healthcare', 'role': 'Research', 'mode': 'Online', 'slots': 2, 'bio': 'Machine learning, research and higher studies.', 'background': 'Applied machine learning in healthcare.', 'linkedin': '', 'approved': True, 'active': True},
            {'id': 4, 'name': 'Rohan Das', 'title': 'Founder', 'field': 'Business', 'industry': 'Education', 'role': 'Founder', 'mode': 'Hybrid', 'slots': 3, 'bio': 'Starting a company and building products.', 'background': 'Founder in education technology.', 'linkedin': '', 'approved': True, 'active': True},
            {'id': 5, 'name': 'Sana Ahmed', 'title': 'UX Researcher', 'field': 'Design', 'industry': 'Technology', 'role': 'Research', 'mode': 'Online', 'slots': 2, 'bio': 'User research and product design.', 'background': 'Research lead for consumer products.', 'linkedin': '', 'approved': False, 'active': True},
        ],
        'requests': [
            {'id': 1, 'student': 'Ishita Rao', 'email': 'ishita@iitm.ac.in', 'mentor': 'Arjun Nair', 'goal': 'I want to explore product analytics roles.', 'message': 'Can we discuss portfolio projects?', 'status': 'Pending', 'term': 'Sep–Dec 2026'}
        ],
        'students': [
            {'name': 'Ananya Menon', 'program': 'BS Data Science', 'mentor': '', 'feedback': '—'},
            {'name': 'Ishita Rao', 'program': 'BS Data Science', 'mentor': '', 'feedback': '—'},
            {'name': 'Rohan Singh', 'program': 'BS Electronic Systems', 'mentor': 'Kavya Iyer', 'feedback': '4 / 5'}
        ],
        'tasks': [{'id': 1, 'student': 'Ananya Menon', 'title': 'Update my project portfolio', 'done': False}],
        'meetings': [], 'messages': [], 'profiles': {}, 'history': [],
        'tickets': [{'id': 1, 'name': 'Rohan Singh', 'role': 'student', 'type': 'Meeting issue', 'description': 'Need help finding a time for the next meeting.', 'status': 'Open', 'reply': ''}],
        'blacklisted': [], 'term': DEFAULT_TERM,
        'communities': [
            {'id': 1, 'name': 'Data Science & ML Hub', 'description': 'Discussions on ML algorithms, deep learning, kaggle competitions, and research.', 'category': 'ML', 'visibility': 'public', 'member_count': 42},
            {'id': 2, 'name': 'FinTech & Quant Careers', 'description': 'Career prep for quantitative finance, financial analytics, and product strategy.', 'category': 'Finance', 'visibility': 'public', 'member_count': 28}
        ],
        'community_messages': [], 'users': []
    }


def get_state() -> dict:
    """Read the persisted application state, falling back to defaults when unavailable."""
    from extensions import sb
    try:
        result = sb.table('app_state').select('payload').eq('id', 1).limit(1).execute()
        if result.data and result.data[0].get('payload'):
            return result.data[0]['payload']
    except Exception as exc:
        current_app.logger.warning('app_state read fallback: %s', exc)
    payload = default_state()
    try:
        sb.table('app_state').upsert({'id': 1, 'payload': payload}).execute()
    except Exception as exc:
        current_app.logger.warning('app_state seed write notice: %s', exc)
    return payload


def save_state(payload: dict) -> None:
    """Persist the application state to Supabase."""
    from extensions import sb
    try:
        sb.table('app_state').upsert({'id': 1, 'payload': payload, 'updated_at': datetime.now(timezone.utc).isoformat()}).execute()
    except Exception as exc:
        current_app.logger.error('Failed to save state to Supabase: %s', exc)
