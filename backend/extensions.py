"""Central Flask extensions and infrastructure clients."""
from __future__ import annotations

from flask import Flask
from flask_cors import CORS
from supabase import Client, create_client

from config import config

app: Flask = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

sb: Client = None  # Service role client (server-side admin operations only)
auth_client: Client = None  # Anon key client (end-user identity operations)


def init_extensions(flask_app: Flask) -> Flask:
    """Initialize CORS and Supabase clients onto the Flask app."""
    flask_app.config['SECRET_KEY'] = config.SECRET_KEY
    CORS(
        flask_app,
        resources={r'/api/*': {'origins': [o.strip() for o in config.FRONTEND_ORIGIN.split(',') if o.strip()]}},
        supports_credentials=True,
    )
    global sb, auth_client
    sb = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
    auth_client = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
    return flask_app


def create_app() -> Flask:
    """Application factory used by app.py when running the service."""
    return init_extensions(app)
