"""Shared AI utilities."""
from __future__ import annotations

from common.ai.client import openrouter_chat, openrouter_embedding, openrouter_text
from common.ai.embeddings import embed_query, embed_text, profile_text, EMBEDDING_DIM
from common.ai.mentor_indexing import analyze_and_index_mentor
from common.ai.retrieval import semantic_search, is_eligible, build_reason
from common.ai.intent_router import is_find_command, parse_command
from common.ai.chat_service import respond as chat_respond
from common.ai.query_enhancer import enhance_query
from common.ai.mentor_rag import run_find, top_explanation

__all__ = [
    'openrouter_chat', 'openrouter_embedding', 'openrouter_text',
    'embed_query', 'embed_text', 'profile_text', 'EMBEDDING_DIM',
    'analyze_and_index_mentor', 'semantic_search', 'is_eligible', 'build_reason',
    'is_find_command', 'parse_command', 'chat_respond', 'enhance_query', 'run_find', 'top_explanation',
]
