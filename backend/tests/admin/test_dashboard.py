"""Admin dashboard & approvals structure tests."""

def test_admin_dashboard_routes_registered(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    for expected in ['/api/admin/dashboard', '/api/admin/mentors/<int:mentor_id>/approve', '/api/admin/users/<int_or_email>/status']:
        assert expected in rules, f'missing {expected}'

def test_admin_dashboard_requires_auth(client):
    assert client.get('/api/admin/dashboard').status_code in (401, 403)
