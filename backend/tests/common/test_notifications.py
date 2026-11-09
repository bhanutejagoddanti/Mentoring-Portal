"""Common notifications structure tests."""

def test_notifications_routes(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    assert '/api/notifications' in rules
    assert client.get('/api/notifications').status_code == 401

def test_meetings_routes(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    assert '/api/meetings' in rules
    assert client.get('/api/meetings').status_code == 401
