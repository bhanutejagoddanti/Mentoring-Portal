"""IITM BS Mentoring Portal - Production Flask Backend."""
from __future__ import annotations

from extensions import create_app
from common.middleware.errors import register_error_handlers

app = create_app()

# Import blueprints AFTER extensions are initialized so route modules bind
# the live Supabase clients (from extensions import auth_client, sb).
from student import student_bp
from mentor import mentor_bp
from admin import admin_bp, matching_bp_full, help_status_bp_full
from common import auth_bp, database_bp, communities_bp, meetings_bp, notifications_bp, messaging_bp

register_error_handlers(app)
for bp in [auth_bp, database_bp, communities_bp, meetings_bp, notifications_bp, messaging_bp]:
    app.register_blueprint(bp)
for bp in [student_bp, mentor_bp, admin_bp, matching_bp_full, help_status_bp_full]:
    app.register_blueprint(bp)


if __name__ == '__main__':
    from config import config

    print(f"Starting IITM BS Mentoring API server on port {config.PORT}...")
    app.run(host='0.0.0.0', port=config.PORT, debug=config.FLASK_DEBUG)
