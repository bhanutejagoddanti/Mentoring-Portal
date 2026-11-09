"""Help workflow route presence + status validation."""

def test_help_routes_registered(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    for expected in [
        '/api/help-requests',
        '/api/help-requests/<int:ticket_id>',
        '/api/help-requests/<int:ticket_id>/messages',
        '/api/help-requests/<int:ticket_id>/status',
        '/api/help-requests/<int:ticket_id>/assign',
        '/api/help-requests/<int:ticket_id>/interventions',
        '/api/admin/help-requests',
        '/api/admin/help-requests/<int:ticket_id>/status',
    ]:
        assert expected in rules, f'missing {expected}'

def test_help_list_unauthorized(client):
    r = client.get('/api/help-requests')
    assert r.status_code == 401
