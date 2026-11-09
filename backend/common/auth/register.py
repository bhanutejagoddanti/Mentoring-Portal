"""Registration route (POST /api/auth/register)."""
from __future__ import annotations

from flask import Blueprint, request

from extensions import sb
from common.database.state import get_state as read_state, save_state as write_state
from common.responses import api_response, error_response

bp = Blueprint('auth_register', __name__)


@bp.post('/register')
def register():
    """Register a new student or mentor account."""
    data = request.get_json() or {}
    role = data.get('role')
    if role not in ('student', 'mentor'):
        return error_response('Role must be student or mentor', 400)
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not name or not email or len(password) < 8:
        return error_response('Full name, valid email, and password of at least 8 characters are required.', 400)
    created = sb.auth.admin.create_user({
        'email': email,
        'password': password,
        'email_confirm': True,
        'user_metadata': {'name': name, 'role': role},
    })
    au = created.user
    approved = (role == 'student')
    try:
        sb.table('user_profiles').upsert({
            'id': au.id, 'email': email, 'name': name, 'role': role,
            'approved': approved, 'active': True,
        }).execute()
    except Exception:
        pass
    if role == 'student':
        try:
            sb.table('student_profiles').upsert({
                'user_id': au.id,
                'program': data.get('program', 'BS Data Science'),
                'level': data.get('level', 'Level 1'),
                'goals': data.get('goals') or '',
            }).execute()
        except Exception:
            pass
    elif role == 'mentor':
        try:
            sb.table('mentor_profiles').upsert({
                'user_id': au.id,
                'title': data.get('job') or '', 'field': data.get('field') or '',
                'industry': data.get('industry') or '', 'role': data.get('job') or '',
                'mode': data.get('mode') or 'Online', 'slots': int(data.get('slots') or 2),
                'bio': data.get('background') or '', 'background': data.get('background') or '',
                'linkedin': data.get('linkedin') or '', 'available': True,
            }).execute()
        except Exception:
            pass
    state = read_state()
    if role == 'mentor':
        state.setdefault('mentors', []).append({
            'id': len(state.get('mentors') or []) + 1, 'user_id': au.id, 'name': name, 'email': email,
            'title': data.get('job') or '', 'field': data.get('field') or '', 'industry': data.get('industry') or '',
            'role': data.get('job') or '', 'mode': data.get('mode') or 'Online', 'slots': int(data.get('slots') or 2),
            'bio': data.get('background') or '', 'background': data.get('background') or '',
            'linkedin': data.get('linkedin') or '', 'approved': False, 'active': True,
        })
        write_state(state)
    return api_response({'message': f'{role.capitalize()} registration submitted successfully. Mentor accounts await IIC Admin approval.'}, status=201)
