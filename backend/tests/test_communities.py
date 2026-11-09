"""Community approval workflow route presence."""

def test_community_routes_registered(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    for expected in [
        '/api/communities',
        '/api/community-requests',
        '/api/community-requests/<int:cid>',
        '/api/community-requests/<int:cid>/approve',
        '/api/community-requests/<int:cid>/reject',
        '/api/community-requests/<int:cid>/request-changes',
    ]:
        assert expected in rules, f'missing {expected}'

def test_community_list_unauthorized(client):
    r = client.get('/api/communities')
    assert r.status_code == 401
