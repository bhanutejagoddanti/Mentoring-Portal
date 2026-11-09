"""Common database service (app_state delegation)."""
from __future__ import annotations
from common.database.state import get_state, save_state
from common.database.profile import get_profile

def read_state() -> dict:
    return get_state()

def write_state(payload: dict) -> None:
    save_state(payload)

def read_profile(user_id: str):
    return get_profile(user_id)
