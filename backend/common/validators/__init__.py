"""Common request validation."""
from __future__ import annotations


def require_fields(data: dict, fields: list, context: str = 'Request') -> str | None:
    """Validate that a JSON payload contains the required fields."""
    for field in fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"{context} is missing required field: {field}"
    return None
