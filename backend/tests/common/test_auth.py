"""Auth endpoint structure tests (no live DB credentials needed for open endpoints)."""

def test_health_open(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    body = r.get_json()
    assert body['status'] == 'ok'

def test_auth_health_open(client):
    r = client.get('/api/auth/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'

def test_login_requires_fields(client):
    r = client.post('/api/auth/login', json={})
    assert r.status_code == 400

def test_me_requires_auth(client):
    r = client.get('/api/auth/me')
    assert r.status_code == 401

def test_mentors_list_requires_auth(client):
    r = client.get('/api/mentors')
    assert r.status_code == 401
