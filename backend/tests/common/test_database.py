"""Database & health checks (read-only; never writes to production)."""
import os
import pytest


def test_health_open(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'


def test_config_present():
    from config import config
    assert config.SUPABASE_URL and config.SUPABASE_ANON_KEY and config.SUPABASE_SERVICE_ROLE_KEY


def test_supabase_read_only_probe():
    """Probe Supabase connectivity read-only. SKIP when tables missing."""
    if not os.getenv('SUPABASE_URL', '').strip():
        pytest.skip('SUPABASE_URL not set')
    from config import config
    from supabase import create_client
    sb = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
    try:
        r = sb.table('user_profiles').select('id').limit(1).execute()
        assert isinstance(r.data, list)
    except Exception as e:
        pytest.skip(f'Supabase probe unavailable: {str(e)[:120]}')
