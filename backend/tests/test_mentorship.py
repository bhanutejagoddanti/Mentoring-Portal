"""Mentorship + core catalogue route presence."""

def test_mentorship_routes_registered(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    for expected in [
        '/api/mentorship-requests',
        '/api/mentorship-requests/<int:req_id>/<decision>',
        '/api/mentors/filter-options',
        '/api/mentors/search',
        '/api/terms/current',
        '/api/state',
    ]:
        assert expected in rules, f'missing {expected}'

def test_filter_options_open(client):
    r = client.get('/api/mentors/filter-options')
    assert r.status_code == 200
    body = r.get_json()
    assert 'fields' in body and 'industries' in body and 'modes' in body
