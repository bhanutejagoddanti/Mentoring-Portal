"""Shared embedding utilities (single responsibility: query/profile embeddings)."""
from __future__ import annotations

from common.ai.client import openrouter_embedding

EMBEDDING_MODEL = 'openai/text-embedding-3-small'
EMBEDDING_DIM = 1536


def embed_text(text: str) -> list[float] | None:
    """Embed arbitrary text (queries and mentor profiles share this path)."""
    return openrouter_embedding(text)


def embed_query(query: str) -> list[float] | None:
    """Embed a student query for vector retrieval (no mentor re-embedding)."""
    return openrouter_embedding((query or '').strip())


def profile_text(mentor: dict) -> str:
    """Serialize a mentor profile for embedding (analysis text, not raw slots)."""
    parts = [
        str(mentor.get('name', '')),
        str(mentor.get('title', '')),
        str(mentor.get('role', '')),
        str(mentor.get('field', '')),
        str(mentor.get('industry', '')),
        str(mentor.get('bio', '')),
        str(mentor.get('background', '')),
        str(mentor.get('experience', '') or mentor.get('years', '')),
        str(mentor.get('education', '')),
        str(mentor.get('career_paths', '') or ''),
        ' '.join(mentor.get('skills', []) if isinstance(mentor.get('skills'), list) else []),
        ' '.join(mentor.get('mentoring_topics', []) if isinstance(mentor.get('mentoring_topics'), list) else []),
    ]
    return ' | '.join(p for p in parts if p.strip())
