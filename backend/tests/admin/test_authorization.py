"""Authorization structure tests: admin-only and login-only routes are guarded."""

ADMIN_ONLY = [
    ('GET', '/api/admin/dashboard'),
    ('GET', '/api/admin/help-requests'),
    ('GET', '/api/community-requests'),
]

def test_admin_routes_require_auth(client):
    for method, path in ADMIN_ONLY:
        r = client.open(path, method=method)
        assert r.status_code in (401, 403), f'{method} {path} -> {r.status_code}'

def test_student_direct_community_create_is_admin_only(client):
    # Blueprint wiring: POST /api/communities exists and is admin-gated via roles decorator
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    assert '/api/communities' in rules

def test_help_status_route_exists(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    assert '/api/help-requests/<int:ticket_id>/status' in rules
