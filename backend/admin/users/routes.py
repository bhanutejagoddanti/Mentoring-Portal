"""Admin user management routes (POST /api/admin/users/<id>/status)."""
from __future__ import annotations

from flask import Blueprint, request

from common.middleware.role import roles
from common.responses import api_response
from admin.users.service import set_account_active

bp = Blueprint('admin_users', __name__)


@bp.post('/users/<int_or_email>/status')
@roles('admin')
def toggle_user_status(int_or_email):
    """Activate or deactivate a user account."""
    return api_response(set_account_active(int_or_email, (request.get_json() or {}).get('active', True)))
