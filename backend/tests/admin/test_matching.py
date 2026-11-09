"""Admin matching & user management structure tests."""

def test_matching_routes(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    assert '/api/mentors/<int:mentor_id>/index' in rules
    assert '/api/admin/users/<int_or_email>/status' in rules
    assert client.post('/api/mentors/1/index', json={}).status_code in (401, 403)
