"""Admin dashboard routes (GET /api/admin/dashboard)."""
from __future__ import annotations

from flask import Blueprint

from common.middleware.role import roles
from common.responses import api_response
from admin.dashboard.service import admin_dashboard

bp = Blueprint('admin_dashboard', __name__)


@bp.get('/dashboard')
@roles('admin')
def admin_dashboard_route():
    """Return aggregate admin dashboard counts."""
    return api_response(admin_dashboard())
