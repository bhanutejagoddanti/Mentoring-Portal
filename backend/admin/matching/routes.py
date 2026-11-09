"""Admin matching routes (POST /api/mentors/<id>/index — URL preserved under mentor prefix)."""
from __future__ import annotations

from flask import Blueprint

from common.middleware.role import roles
from common.responses import api_response, error_response
from admin.matching.service import index_mentor

bp = Blueprint('admin_matching', __name__)


@bp.post('/<int:mentor_id>/index')
@roles('admin')
def admin_index_mentor(mentor_id: int):
    """Generate AI profile analysis and embedding for an approved mentor."""
    result = index_mentor(mentor_id)
    if result.get('error'):
        return error_response(result['error'], result.get('status', 400))
    return api_response(result)
