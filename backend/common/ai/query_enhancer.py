"""Query enhancer (single responsibility: /find query understanding)."""
from __future__ import annotations

import re

from common.ai.client import openrouter_chat

FALLBACK_STOPWORDS = {'i', 'need', 'a', 'an', 'the', 'in', 'for', 'and', 'with', 'to', 'of', 'mentor', 'mentoring'}


def _regex_skills(query: str) -> list[str]:
    skills = []
    for cand in ['Machine Learning', 'Python', 'Deep Learning', 'Data Science', 'Product', 'Cloud', 'JavaScript', 'React']:
        if cand.lower() in query.lower():
            skills.append(cand)
    return skills


def enhance_query(query: str) -> dict:
    """Enhance a /find query without changing intent.

    Returns dict with enhanced_query plus extracted dimensions. Falls back to
    the original query when the LLM is unavailable (never fabricates).
    """
    original = (query or '').strip()
    if not original:
        return {'enhanced_query': '', 'skills': [], 'expertise': [], 'industry': '', 'role': '', 'career_goals': '', 'mentoring_requirements': ''}
    prompt = (
        'You enhance a student mentor-search query. Preserve intent exactly. '
        'Return strict JSON only with keys: enhanced_query (string, enriched but faithful), '
        'skills (array of strings), expertise (array), industry (string), role (string), '
        'career_goals (string), mentoring_requirements (string). '
        f'Student query: {original}'
    )
    llm = openrouter_chat(prompt)
    if isinstance(llm, dict) and llm.get('enhanced_query'):
        enhanced = str(llm['enhanced_query']).strip() or original
        return {
            'enhanced_query': enhanced,
            'skills': [str(x) for x in (llm.get('skills') or []) if str(x).strip()],
            'expertise': [str(x) for x in (llm.get('expertise') or []) if str(x).strip()],
            'industry': str(llm.get('industry') or ''),
            'role': str(llm.get('role') or ''),
            'career_goals': str(llm.get('career_goals') or ''),
            'mentoring_requirements': str(llm.get('mentoring_requirements') or ''),
        }
    enhanced = original
    skills = _regex_skills(original)
    if skills:
        enhanced = f"{original} — seeking mentors strong in {', '.join(skills)}"
    goals = original
    return {'enhanced_query': enhanced, 'skills': skills, 'expertise': [], 'industry': '', 'role': '', 'career_goals': goals, 'mentoring_requirements': ''}
