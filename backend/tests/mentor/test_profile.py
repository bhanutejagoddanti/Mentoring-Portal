"""Mentor profile / availability structure tests."""

def test_mentor_routes_registered(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    for expected in ['/api/mentors', '/api/mentors/filter-options', '/api/mentors/search', '/api/mentors/<int:mentor_id>/index']:
        assert expected in rules, f'missing {expected}'

def test_mentor_search_envelope(client):
    r = client.post('/api/mentors/search', json={'query': '', 'limit': 5})
    assert r.status_code == 200
    body = r.get_json()
    assert 'items' in body
    assert all('vector' not in i.get('mentor', {}) for i in body['items'])
