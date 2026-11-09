"""Common exception mapping (single responsibility: API error translation)."""
from __future__ import annotations


class ApiError(Exception):
    """Typed API error carrying an HTTP status."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status
