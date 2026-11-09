"""Student community participation service (join/discovery delegates to common)."""
from __future__ import annotations

from common.communities.membership import visible_communities, join_community, leave_community
from common.communities.messaging import list_messages
from common.database.state import get_state

def browse(user: dict) -> list:
    return visible_communities(get_state(), user)

def join(cid: int, user: dict) -> dict:
    return join_community(cid, user)

def leave(cid: int, user: dict) -> dict:
    return leave_community(cid, user)

def messages(cid: int) -> list:
    return list_messages(cid)
