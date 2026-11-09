"""Student history routes (GET /api/students/<id>/history)."""
from __future__ import annotations

from flask import Blueprint

from common.middleware.auth import login_required
from common.responses import api_response
from student.history.service import history_for

bp = Blueprint('student_history', __name__)


@bp.get('/<int:student_id>/history')
@login_required
def student_history(student_id: int):
    """Return mentorship history for a student."""
    return api_response(items=history_for(student_id))
