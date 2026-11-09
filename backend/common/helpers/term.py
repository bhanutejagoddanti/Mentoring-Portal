"""Term formatting helpers (single responsibility: academic term labels)."""
from __future__ import annotations

from datetime import datetime

from common.helpers.constants import TERM_MONTHS


def term_label(start: str = '', end: str = '') -> str:
    """Format an academic term range the same way the React frontend does, e.g. 'Sep–Dec 2026'."""

    def _parse(value):
        try:
            return datetime.fromisoformat(str(value))
        except Exception:
            return None

    start_date = _parse(start)
    end_date = _parse(end)
    if not start_date or not end_date:
        fallback = f"{start}–{end}".replace('–', '-').strip()
        return fallback or 'Current term'
    if start_date.year == end_date.year:
        return f"{TERM_MONTHS[start_date.month - 1]}–{TERM_MONTHS[end_date.month - 1]} {start_date.year}"
    return f"{TERM_MONTHS[start_date.month - 1]} {start_date.year}–{TERM_MONTHS[end_date.month - 1]} {end_date.year}"
