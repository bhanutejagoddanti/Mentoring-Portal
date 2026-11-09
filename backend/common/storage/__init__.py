"""Common file storage (mentoring-files bucket helpers)."""
from __future__ import annotations


def ticket_file_path(help_request_id, file_name: str) -> str:
    """Return the storage object path for a help attachment."""
    return f"help-requests/{help_request_id}/{file_name}"


def community_file_path(request_id, file_name: str) -> str:
    """Return the storage object path for a community supporting file."""
    return f"community-requests/{request_id}/{file_name}"
