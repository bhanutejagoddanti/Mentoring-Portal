"""Mentor blueprint aggregator.

Mentor dashboard features with unique URLs live here; shared URLs
(communities/meetings/notifications/help canonical) are registered once in
common/student and imported by role.
"""
from __future__ import annotations

from flask import Blueprint

mentor_bp = Blueprint('mentor', __name__)

__all__ = ['mentor_bp']
