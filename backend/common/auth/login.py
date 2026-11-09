"""Login route (POST /api/auth/login)."""
from __future__ import annotations

from flask import Blueprint, request

from extensions import auth_client, sb
from common.responses import api_response, error_response

bp = Blueprint('auth_login', __name__)


@bp.post('/login')
def login():
    """Authenticate a user and return access / refresh tokens."""
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not email or not password:
        return error_response('Email and password are required', 400)
    try:
        res = auth_client.auth.sign_in_with_password({'email': email, 'password': password})
        au = res.user
        profile = None
        try:
            profile_rows = sb.table('user_profiles').select('*').eq('id', au.id).limit(1).execute().data
            profile = profile_rows[0] if profile_rows else None
        except Exception:
            profile = None
        name = profile['name'] if profile else au.user_metadata.get('name', 'User')
        role = profile['role'] if profile else au.user_metadata.get('role', 'student')
        active = profile.get('active', True) if profile else True
        approved = profile.get('approved', True) if profile else True
        if not active:
            return error_response('This account has been deactivated. Please contact the IIC Admin.', 403)
        if role == 'mentor' and not approved:
            return error_response('Your mentor registration is pending IIC Admin approval. You will receive access once approved.', 403)
        return api_response({
            'access_token': res.session.access_token,
            'refresh_token': res.session.refresh_token,
            'user': {'id': au.id, 'name': name, 'email': au.email, 'role': role, 'approved': approved},
        })
    except Exception:
        return error_response('Incorrect email or password. Please verify your credentials.', 401)
