"""Common auth blueprint (lazy submodule registration)."""
from __future__ import annotations


def __getattr__(name):
    if name == 'auth_bp':
        from flask import Blueprint
        from common.auth.register import bp as register_bp
        from common.auth.login import bp as login_bp
        from common.auth.session import bp as session_bp
        bp = Blueprint('auth', __name__, url_prefix='/api/auth')
        bp.register_blueprint(register_bp)
        bp.register_blueprint(login_bp)
        bp.register_blueprint(session_bp)
        return bp
    raise AttributeError(name)


__all__ = ['auth_bp']
