"""Intent router (single responsibility: /find command detection)."""
from __future__ import annotations


def parse_command(message: str) -> tuple[bool, str]:
    """Return (is_find, query). Handles `/find`, `/Find`, leading whitespace."""
    text = (message or '').strip()
    if text.lower().startswith('/find'):
        rest = text[5:]  # after '/find'
        # '/findXYZ' is not a command; require boundary or empty
        if rest and not rest[0].isspace():
            return False, text
        return True, rest.strip()
    return False, text


def is_find_command(message: str) -> bool:
    return parse_command(message)[0]
