"""Mentor AI indexing (single responsibility: profile analysis + vector write)."""
from __future__ import annotations

from datetime import datetime, timezone

from extensions import sb
from common.ai.client import openrouter_chat, openrouter_embedding
from common.ai.embeddings import profile_text


def analyze_and_index_mentor(mentor: dict) -> dict:
    """Analyze a mentor profile and persist the semantic vector when available.

    Writes: mentor['ai_profile'] + mentor['vector'] in app_state (source of
    truth for retrieval) and best-effort rows in mentor_profiles.ai_profile /
    mentor_vectors.embedding when relational tables exist.

    Existing rich ai_profile is preserved when the LLM call fails (never
    downgraded to the baseline template).
    """
    from flask import current_app

    base_text = profile_text(mentor)
    existing = mentor.get('ai_profile') or {}
    baseline = {
        'skills': [mentor.get('field') or ''] if mentor.get('field') else [],
        'industries': [mentor.get('industry') or ''] if mentor.get('industry') else [],
        'roles': [mentor.get('title') or mentor.get('role') or ''],
        'mentoring_topics': ['Career Guidance', 'Project Reviews', 'Interview Prep'],
        'career_paths': [mentor.get('field') or ''],
    }
    analysis = dict(existing) if isinstance(existing, dict) and existing else dict(baseline)
    llm_analysis = openrouter_chat(
        'Analyze this mentor profile and return strict JSON with keys: skills (array of strings), industries (array), roles (array), experience (string), education (string), career_paths (array), mentoring_topics (array), summary (short string). Use only facts present in the profile.\n\nProfile:\n' + str(base_text)
    )
    if llm_analysis and isinstance(llm_analysis, dict):
        analysis.update(llm_analysis)

    embedding_text = f"{base_text} | Topics: {', '.join(analysis.get('mentoring_topics') or [])} | Skills: {', '.join(analysis.get('skills') or [])} | Paths: {', '.join(analysis.get('career_paths') or [])} | Industries: {', '.join(analysis.get('industries') or [])}"
    vector = openrouter_embedding(embedding_text)
    mentor['ai_profile'] = analysis
    if vector:
        mentor['vector'] = vector
    mentor['profile_indexed_at'] = datetime.now(timezone.utc).isoformat()
    # Best-effort relational persistence (tables may not exist in this project DB).
    if mentor.get('user_id'):
        try:
            m_prof = sb.table('mentor_profiles').select('id').eq('user_id', mentor['user_id']).limit(1).execute()
            if m_prof.data:
                m_id = m_prof.data[0]['id']
                if vector:
                    sb.table('mentor_vectors').upsert({
                        'mentor_id': m_id, 'embedding': vector,
                        'extracted_metadata': analysis,
                        'updated_at': datetime.now(timezone.utc).isoformat(),
                    }).execute()
                try:
                    sb.table('mentor_profiles').update({'ai_profile': analysis, 'profile_indexed_at': datetime.now(timezone.utc).isoformat()}).eq('id', m_id).execute()
                except Exception:
                    pass
        except Exception as exc:
            current_app.logger.warning('pgvector mentor_vectors write notice: %s', exc)
    return {'indexed': True, 'analysis': analysis, 'has_embedding': vector is not None, 'vector_dim': len(vector) if vector else 0}
