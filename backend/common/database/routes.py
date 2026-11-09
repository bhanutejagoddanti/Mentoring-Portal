"""Shared database/state routes (health, terms, state lifecycle)."""
from __future__ import annotations

from flask import Blueprint, request

from common.database.state import get_state, save_state
from common.middleware.auth import login_required
from common.responses import api_response, error_response

bp = Blueprint('common_database', __name__, url_prefix='/api')


@bp.get('/health')
def health():
    """Health check for the backend and frontend integration."""
    from config import config
    return api_response({'status': 'ok', 'openrouter_configured': bool(config.OPENROUTER_API_KEY), 'openrouter_model': config.OPENROUTER_MODEL})


@bp.get('/terms/current')
@login_required
def current_term():
    """Return the current academic term window."""
    return api_response(get_state().get('term', {}))


@bp.get('/state')
@login_required
def read_state_route():
    """Read the full application state."""
    return api_response(get_state())


def _preserve_vectors(payload: dict) -> dict:
    """Never let a client full-state sync wipe precomputed RAG vectors/ai_profile.

    If an incoming mentor lacks vector/ai_profile but the stored mentor has them,
    carry the stored values forward (vectors are precomputed; see sessions).
    """
    try:
        existing = get_state()
        stored = {m.get('name'): m for m in existing.get('mentors') or []}
        for m in payload.get('mentors') or []:
            keep = stored.get(m.get('name'))
            if keep and not m.get('vector') and keep.get('vector'):
                m['vector'] = keep['vector']
            if keep and not m.get('ai_profile') and keep.get('ai_profile'):
                m['ai_profile'] = keep['ai_profile']
            if keep and not m.get('profile_indexed_at') and keep.get('profile_indexed_at'):
                m['profile_indexed_at'] = keep['profile_indexed_at']
    except Exception:
        pass
    return payload


@bp.put('/state')
@login_required
def write_state_route():
    """Write the full application state (preserving RAG vectors)."""
    payload = request.get_json()
    if not isinstance(payload, dict):
        return error_response('State must be a JSON object', 400)
    save_state(_preserve_vectors(payload))
    return api_response({'message': 'State synchronized with Supabase PostgreSQL'})
