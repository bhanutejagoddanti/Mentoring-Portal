"""Global error handling (single responsibility: JSON error envelopes)."""
from __future__ import annotations

from flask import jsonify


def register_error_handlers(app) -> None:
    """Register JSON error handlers for the Flask application."""

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error='Endpoint not found'), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify(error='Method not allowed'), 405

    @app.errorhandler(500)
    def server_error(exc):
        app.logger.exception('Unhandled server error: %s', exc)
        return jsonify(error='Internal server error'), 500
