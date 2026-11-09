"""Common response formatting (consistent JSON envelopes)."""
from __future__ import annotations

from flask import jsonify


def api_response(data=None, status: int = 200, error: str | None = None, **kwargs):
    """Return a consistent JSON envelope, merging keyword arguments into the body."""
    body = dict(data) if isinstance(data, dict) else (dict(data) if data is not None else {})
    if error:
        body['error'] = error
    for key, value in kwargs.items():
        body[key] = value
    return jsonify(body), status


def error_response(message: str, status: int = 400):
    """Return a consistent JSON error envelope."""
    return jsonify(error=message), status
