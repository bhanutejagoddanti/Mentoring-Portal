"""Shared helper + response envelope tests."""

def test_api_response_envelope():
    from common.responses import api_response
    from app import app as flask_app
    with flask_app.test_request_context():
        resp, status = api_response({'items': [1]})
        assert status == 200
        assert resp.get_json() == {'items': [1]}

def test_api_response_merges_kwargs():
    from common.responses import api_response
    from app import app as flask_app
    with flask_app.test_request_context():
        resp, status = api_response(items=[1], total=1)
        body = resp.get_json()
        assert body == {'items': [1], 'total': 1}

def test_term_label():
    from common.helpers.term import term_label
    assert term_label('2026-09-01', '2026-12-20') == 'Sep–Dec 2026'
