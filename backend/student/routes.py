"""Student blueprint aggregator (registered as one of four main blueprints)."""
from __future__ import annotations

from flask import Blueprint

from student.profile.routes import bp as profile_bp
from student.history.routes import bp as history_bp
from student.mentor_search.routes import bp as search_bp
from student.mentor_search.mentors_route import bp as search_alias_bp
from student.mentor_search.chat import bp as chat_bp
from student.mentorship.routes import bp as mentorship_bp
from student.help.routes import bp as help_bp

student_bp = Blueprint('student', __name__)

student_bp.register_blueprint(profile_bp, url_prefix='/api/students')
student_bp.register_blueprint(history_bp, url_prefix='/api/students')
student_bp.register_blueprint(search_bp, url_prefix='/api/mentors')
student_bp.register_blueprint(search_alias_bp, url_prefix='/api/search')
student_bp.register_blueprint(chat_bp, url_prefix='/api/mentors')
student_bp.register_blueprint(mentorship_bp, url_prefix='/api/mentorship-requests')
student_bp.register_blueprint(help_bp, url_prefix='/api/help-requests')

__all__ = ['student_bp']
