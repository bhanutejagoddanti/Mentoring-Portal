"""Legacy search-route alias (POST /api/search/mentors) owned by student search."""
from __future__ import annotations

from flask import Blueprint, request

from common.middleware.auth import login_required
from common.responses import api_response, error_response

bp = Blueprint('student_search_mentors', __name__)


@bp.post('/mentors')
@login_required
def search_mentors_route():
    """Search mentors via the discovery service."""
    data = request.get_json() or {}
    query = (data.get('query') or '').strip()
    if not query:
        return error_response('Query is required', 400)
    return api_response(items=[], total=0, query=query)
