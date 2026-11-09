"""Student community routes (re-exports common discovery under student blueprint docs).

Actual URL registration lives in common/communities; this module documents the
student surface and is intentionally empty of duplicate rules.
"""
from __future__ import annotations

from flask import Blueprint

bp = Blueprint('student_communities', __name__)
