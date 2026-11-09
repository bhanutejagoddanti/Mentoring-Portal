"""Application configuration for the IITM BS Mentoring Portal."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


@dataclass(frozen=True)
class Config:
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SECRET_KEY: str
    FRONTEND_ORIGIN: str
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str
    PORT: int
    FLASK_DEBUG: bool

    @classmethod
    def from_env(cls) -> "Config":
        supabase_url = os.getenv('SUPABASE_URL', '').strip()
        if '/rest/v1' in supabase_url:
            supabase_url = supabase_url.split('/rest/v1')[0].rstrip('/')
        return cls(
            SUPABASE_URL=supabase_url,
            SUPABASE_ANON_KEY=os.getenv('SUPABASE_ANON_KEY', '').strip(),
            SUPABASE_SERVICE_ROLE_KEY=os.getenv('SUPABASE_SERVICE_ROLE_KEY', '').strip(),
            SECRET_KEY=os.getenv('SECRET_KEY', 'change-me'),
            FRONTEND_ORIGIN=os.getenv('FRONTEND_ORIGIN', 'http://localhost:5173'),
            OPENROUTER_API_KEY=os.getenv('OPENROUTER_API_KEY', '').strip(),
            OPENROUTER_MODEL=os.getenv('OPENROUTER_MODEL', 'openrouter/free').strip(),
            PORT=int(os.getenv('PORT', 5001)),
            FLASK_DEBUG=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
        )

    def validate(self) -> None:
        missing = [
            key
            for key in ('SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY')
            if not getattr(self, key)
        ]
        if missing:
            raise RuntimeError(
                f"Required configuration missing: {', '.join(missing)} must be set in backend/.env"
            )


config = Config.from_env()
config.validate()
