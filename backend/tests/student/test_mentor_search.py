"""Student semantic search tests (structure + envelope, no live LLM required)."""

def test_search_route_structure(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    assert '/api/mentors/search' in rules
    assert '/api/mentors/filter-options' in rules

def test_search_requires_query_envelope(client):
    # Unauthenticated search still works (route is public per original contract);
    # empty query must return 200 with keyword method, never 500.
    r = client.post('/api/mentors/search', json={'query': '', 'limit': 5})
    assert r.status_code == 200
    body = r.get_json()
    assert 'items' in body
    assert 'search_method' not in body  # internals stay backend-only
    assert all('vector' not in i.get('mentor', {}) for i in body['items'])
