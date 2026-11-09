"""Student mentor search routes (AI semantic search + catalogue + filters)."""
from __future__ import annotations

from flask import Blueprint, request

from common.auth.user import current_user
from common.middleware.auth import login_required
from common.responses import api_response
from student.mentor_search.service import catalogue, filter_options, semantic_search

bp = Blueprint('student_mentor_search', __name__)


@bp.get('')
@login_required
def list_mentor_catalog():
    """List approved mentors (student dashboard browser)."""
    items = catalogue()
    return api_response(items=items, total=len(items))


@bp.get('/filter-options')
def mentor_filter_options():
    """Filter options for student discovery."""
    options = filter_options()
    return api_response(fields=options['fields'], industries=options['industries'], modes=options['modes'])


@bp.post('/search')
def mentor_search():
    """AI semantic mentor search (RAG: pgvector/cosine over precomputed vectors, top 5)."""
    data = request.get_json() or {}
    query = (data.get('query') or '').strip()
    filters = data.get('filters') or {}
    # Support flat filter fields as well as nested filters.
    for k in ('field', 'industry', 'mode'):
        if data.get(k) and k not in filters:
            filters[k] = data.get(k)
    limit = int(data.get('limit') or 5)
    limit = max(1, min(5, limit))
    try:
        user = current_user()
    except Exception:
        user = None
    result = semantic_search(query=query, filters=filters, limit=limit, user=user)
    return api_response(result)
