"""End-to-end read-path tests (isolated, read-only).

Live *writing* E2E is explicitly opt-in (env UNIT_TEST_LIVE_WRITES=1) and
SKIPs otherwise so production Supabase records are never mutated by CI.
"""
import os
import pytest


def test_e2e_health_to_catalogue(client):
    # health -> filter-options -> search envelope (full stack, no writes)
    assert client.get('/api/health').status_code == 200
    assert client.get('/api/mentors/filter-options').status_code == 200
    r = client.post('/api/mentors/search', json={'query': 'machine learning', 'limit': 5})
    assert r.status_code == 200
    body = r.get_json()
    assert 'items' in body
    assert all('vector' not in i.get('mentor', {}) for i in body['items'])
    assert len(body['items']) <= 5


def test_e2e_unauth_flow(client):
    assert client.get('/api/auth/me').status_code == 401
    assert client.get('/api/help-requests').status_code == 401
    assert client.get('/api/communities').status_code == 401


def test_e2e_live_write_opt_in():
    if os.getenv('UNIT_TEST_LIVE_WRITES') != '1':
        pytest.skip('Live write E2E disabled (set UNIT_TEST_LIVE_WRITES=1 with test-only data)')
