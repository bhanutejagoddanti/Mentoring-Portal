"""AI Career Assistant chat routes.

POST /api/mentors/chat {message, history}
- `/find ...` -> RAG mentor discovery (internal query enhancement stays backend-only)
- anything else -> general career chat (no vector search)
"""
from __future__ import annotations

from flask import Blueprint, request

from common.ai.chat_service import respond as chat_respond
from common.ai.intent_router import parse_command
from common.ai.mentor_rag import run_find
from common.responses import api_response

bp = Blueprint('student_mentor_chat', __name__)


@bp.post('/chat')
def mentor_chat():
    """Conversational career assistant with explicit /find mentor search."""
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    history = data.get('history') or []
    filters = data.get('filters') or {}
    is_find, query = parse_command(message)
    if is_find:
        if not query:
            return api_response({
                'mode': 'clarification',
                'reply': 'Sure — what kind of mentor are you looking for? For example: `/find mentor for Python and data science projects`.',
                'items': [], 'total': 0,
            })
        try:
            user = None
            try:
                from common.auth.user import current_user
                user = current_user()
            except Exception:
                user = None
            result = run_find(query=query, filters=filters, limit=5, user=user)
            return api_response(result)
        except Exception as exc:
            return api_response({'mode': 'error', 'reply': f"We couldn't complete that search right now. Please try again in a moment.", 'message': f"We couldn't complete that search right now. Please try again in a moment.", 'items': [], 'total': 0}, status=500)
    result = chat_respond(message, history=history)
    return api_response({'mode': 'chat', 'reply': result.get('reply', ''), 'items': [], 'total': 0})
