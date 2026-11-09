"""Community repository for the IITM BS Mentoring Portal backend."""
from __future__ import annotations
from extensions import sb

def _safe(fn, label):
    try:
        return fn()
    except Exception as exc:
        try:
            from flask import current_app
            current_app.logger.warning('%s notice: %s', label, exc)
        except Exception:
            pass
        return None

def insert_community_request(request: dict) -> None:
    """Persist a community creation request (best-effort, state is source of truth)."""
    row = {
        'requester_id': request.get('requester_id'),
        'requester_name': request.get('requester_name'),
        'requester_role': request.get('requester_role'),
        'community_name': request.get('community_name'),
        'description': request.get('description'),
        'category': request.get('category', 'General'),
        'purpose': request.get('purpose'),
        'target_audience': request.get('target_audience'),
        'community_type': request.get('community_type', 'Discussion'),
        'reason': request.get('reason'),
        'suggested_moderators': request.get('suggested_moderators') or [],
        'supporting_info': request.get('supporting_info') or '',
        'status': 'Pending',
    }
    _safe(lambda: sb.table('community_requests').insert(row).execute(), 'community_requests insert')

def insert_community_review(review: dict) -> None:
    """Persist a community request review / decision (best-effort)."""
    _safe(lambda: sb.table('community_request_reviews').insert(review).execute(), 'community_request_reviews insert')
