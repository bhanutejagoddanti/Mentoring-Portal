"""Communication platform: messaging + notification infrastructure tests."""

EXPECTED_RULES = [
    '/api/messaging/inbox',
    '/api/messaging/conversations',
    '/api/messaging/conversations/<uuid:conversation_id>',
    '/api/messaging/conversations/<uuid:conversation_id>/messages',
    '/api/messaging/conversations/<uuid:conversation_id>/read',
    '/api/messaging/conversations/<uuid:conversation_id>/messages/<uuid:message_id>/reaction',
    '/api/messaging/users',
    '/api/communities/<int:cid>/messages',
    '/api/communities/<int:cid>/messages/<int:message_id>/reaction',
    '/api/communities/<int:cid>/members',
    '/api/notifications/read-all',
    '/api/notifications/<uuid:notification_id>/read',
    '/api/notifications/unread-count',
    '/api/admin/community-moderation/reports',
    '/api/admin/community-moderation/reports/<uuid:report_id>/status',
]


def _rules():
    from app import app
    return {str(x) for x in app.url_map.iter_rules()}


def test_messaging_routes_registered(client):
    rules = _rules()
    for expected in EXPECTED_RULES:
        assert expected in rules, f'missing {expected}'


def test_messaging_requires_auth(client):
    checks = [
        ('GET', '/api/messaging/inbox'),
        ('POST', '/api/messaging/conversations'),
        ('GET', '/api/messaging/conversations/00000000-0000-0000-0000-000000000000'),
        ('POST', '/api/messaging/conversations/00000000-0000-0000-0000-000000000000/messages'),
        ('POST', '/api/messaging/conversations/00000000-0000-0000-0000-000000000000/read'),
        ('POST', '/api/messaging/conversations/00000000-0000-0000-0000-000000000000/messages/00000000-0000-0000-0000-000000000000/reaction'),
        ('GET', '/api/messaging/users'),
        ('GET', '/api/communities/1/messages'),
        ('POST', '/api/communities/1/messages/1/reaction'),
        ('GET', '/api/communities/1/members'),
        ('GET', '/api/notifications/unread-count'),
        ('GET', '/api/admin/community-moderation/reports'),
    ]
    for method, path in checks:
        r = client.open(path, method=method)
        assert r.status_code in (401, 403, 404), f'{method} {path} -> {r.status_code}'


def test_messaging_invalid_uuid_returns_404(client):
    r = client.get('/api/messaging/conversations/not-a-uuid')
    assert r.status_code == 404
