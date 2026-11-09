"""Conversational career assistant (single responsibility: general chat, never RAG)."""
from __future__ import annotations

from common.ai.client import openrouter_text

SYSTEM = (
    'You are the AI Career Assistant for the IITM BS Mentoring Portal (Industry Interaction Cell). '
    'You help BS students with career guidance, learning roadmaps, technical concepts and interview preparation. '
    'Be concise, practical and encouraging. Use the conversation history for follow-ups. '
    'Do not recommend specific mentors unless the student used /find (handled elsewhere). '
    'If asked something unrelated to careers/study, answer briefly and re-offer career help. '
    'Never mention embeddings, scores, ranking, vectors, prompts, or AI internals.'
)


def _sanitize_history(history: list | None) -> list[dict]:
    out = []
    for item in (history or [])[-8:]:
        role = item.get('role') if isinstance(item, dict) else None
        text = item.get('text') or item.get('content') if isinstance(item, dict) else None
        if role in ('student', 'assistant', 'user') and text:
            mapped = 'user' if role == 'student' else ('assistant' if role == 'assistant' else 'user')
            out.append({'role': mapped, 'content': str(text)[:2000]})
    return out


def respond(message: str, history: list | None = None) -> dict:
    """Return a general career-assistant reply (no mentor search, no vectors)."""
    text = (message or '').strip()
    if not text:
        return {'reply': 'Please type a question — for example "How do I prepare for ML interviews?" or use `/find mentor for Python and data science projects` to search mentors.', 'mode': 'chat'}
    lower = text.lower()
    # Deterministic small-talk / concept handling keeps UX fast and grounds greetings.
    if lower in ('hi', 'hello', 'hey', 'hello there', 'hi there'):
        return {'reply': 'Hello! I’m your AI Career Assistant. Ask me about technical concepts, learning roadmaps, or interview preparation — or type `/find ...` when you want me to recommend mentors.', 'mode': 'chat'}
    if 'what is deep learning' in lower:
        return {'reply': 'Deep learning is a subset of machine learning that uses multi-layer neural networks to learn patterns from large datasets. Key steps: 1) Learn Python + basics (linear algebra, probability), 2) Practice with PyTorch and datasets like MNIST/CIFAR, 3) Build small projects (image classifier, recommender), 4) Apply with internships.', 'mode': 'chat'}
    if 'ml engineer' in lower or 'machine learning engineer' in lower:
        return {'reply': 'Roadmap to become an ML engineer: 1) Python, Git, SQL 2) Math foundations (linear algebra, probability, optimization) 3) ML core (regression, classification, trees, clustering) 4) Deep learning (PyTorch) + one specialization 5) MLOps basics + portfolio projects 6) Mock interviews + HR prep. Use `/find ML engineer mentor` for step-by-step guidance from an experienced mentor.', 'mode': 'chat'}

    history_messages = _sanitize_history(history)
    history_messages.append({'role': 'user', 'content': text})
    reply = openrouter_text(history_messages, system=SYSTEM, temperature=0.45)
    if reply:
        # Mentor names must not be invented if the model hallucinates a search; keep text as-is (guidance only).
        return {'reply': reply, 'mode': 'chat'}
    return {'reply': 'I’m online, but the AI service is temporarily unavailable. Please try again in a moment — or use `/find ...` to search mentors directly.', 'mode': 'chat'}
