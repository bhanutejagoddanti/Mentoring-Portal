"""Admin blueprint aggregator."""
from __future__ import annotations

from flask import Blueprint

from admin.dashboard.routes import bp as dashboard_bp
from admin.users.routes import bp as users_bp
from admin.mentor_approvals.routes import bp as approvals_bp
from admin.help_management.routes import bp as help_bp
from admin.matching.routes import bp as matching_bp
from admin.help_management.status_routes import bp as help_status_bp
from admin.community_moderation.routes import bp as community_moderation_bp

# admin_bp exposes /api/admin/* plus the legacy mentor index URL.
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
admin_bp.register_blueprint(dashboard_bp)
admin_bp.register_blueprint(users_bp)
admin_bp.register_blueprint(approvals_bp)
admin_bp.register_blueprint(help_bp)
admin_bp.register_blueprint(community_moderation_bp)

# Mentor indexing URL is owned by admin matching; registered under /api/mentors prefix.
matching_bp_full = Blueprint('admin_matching_full', __name__, url_prefix='/api/mentors')
matching_bp_full.register_blueprint(matching_bp)
help_status_bp_full = Blueprint('admin_help_status_full', __name__, url_prefix='/api/help-requests')
help_status_bp_full.register_blueprint(help_status_bp)

__all__ = ['admin_bp', 'matching_bp_full', 'help_status_bp_full']
