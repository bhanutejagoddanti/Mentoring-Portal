"""Session routes (health, me, logout, password reset)."""
from __future__ import annotations

from flask import Blueprint, request

from extensions import auth_client
from common.middleware.auth import login_required
from common.auth.user import bearer_token as get_bearer_token
from common.auth.user import current_user
from common.responses import api_response, error_response

bp = Blueprint('auth_session', __name__)


@bp.get('/health')
def health():
    """Health check used by the frontend and monitoring."""
    from config import config

    return api_response({
        'status': 'ok',
        'storage_ready': True,
        'openrouter_configured': bool(config.OPENROUTER_API_KEY),
        'openrouter_model': config.OPENROUTER_MODEL,
    })


@bp.get('/me')
@login_required
def me():
    """Return the current authenticated user."""
    return api_response(user=current_user())


@bp.post('/logout')
def logout():
    """Sign out the current session."""
    token = get_bearer_token()
    if token:
        try:
            auth_client.auth.sign_out(token)
        except Exception:
            pass
    return api_response({'message': 'Logged out successfully'})


@bp.post('/password-reset')
def password_reset():
    """Request a password reset email for the given address."""
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return error_response('Email is required', 400)
    try:
        auth_client.auth.reset_password_for_email(email)
        return api_response({'message': f'If an account exists for {email}, a password reset link has been sent.'})
    except Exception as exc:
        return error_response(str(exc), 400)
