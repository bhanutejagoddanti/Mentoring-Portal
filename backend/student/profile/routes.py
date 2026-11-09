"""Student profile routes (GET /api/students)."""
from __future__ import annotations

from flask import Blueprint

from common.middleware.auth import login_required
from common.responses import api_response
from student.profile.service import list_students

bp = Blueprint('student_profile', __name__)


@bp.get('')
@login_required
def list_students_route():
    """List the student roster (used by student & admin dashboards)."""
    items = list_students()
    return api_response(items=items, total=len(items))
