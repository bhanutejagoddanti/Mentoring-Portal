"""Common mentor matching utilities (cosine similarity + search filters)."""
from __future__ import annotations


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Compute cosine similarity between two numeric vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = sum(a * a for a in v1) ** 0.5
    n2 = sum(b * b for b in v2) ** 0.5
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    return dot / (n1 * n2)


def pass_search_filters(mentor: dict, filters: dict) -> bool:
    """Eligibility-safe manual filter predicate (field/industry/mode)."""
    filters = filters or {}
    field = filters.get('field') or ''
    industry = filters.get('industry') or ''
    mode = filters.get('mode') or ''
    if field and str(mentor.get('field') or '').lower() != str(field).lower():
        return False
    if industry and str(mentor.get('industry') or '').lower() != str(industry).lower():
        return False
    if mode and str(mentor.get('mode') or '').lower() != str(mode).lower():
        return False
    return True
