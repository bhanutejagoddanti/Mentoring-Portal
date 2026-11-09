"""Common auth service (request-scoped delegation)."""
from __future__ import annotations
from common.auth.user import bearer_token, current_user

def get_bearer_token() -> str | None:
    return bearer_token()

def get_current_user() -> dict | None:
    return current_user()
