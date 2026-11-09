"""Mentor approval routes (POST /api/admin/mentors/<id>/approve)."""
from __future__ import annotations

from flask import Blueprint

from common.middleware.role import roles
from common.responses import api_response, error_response
from admin.mentor_approvals.service import approve_mentor

bp = Blueprint('admin_mentor_approvals', __name__)


@bp.post('/mentors/<int:mentor_id>/approve')
@roles('admin')
def approve_mentor_route(mentor_id: int):
    """Approve a mentor (indexing remains an explicit admin action)."""
    result = approve_mentor(mentor_id)
    if result.get('error'):
        return error_response('Mentor not found', 404)
    return api_response(result)
