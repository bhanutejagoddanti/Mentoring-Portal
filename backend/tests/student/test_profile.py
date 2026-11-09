"""Student profile & history structure tests."""

def test_student_profile_routes_registered(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    assert '/api/students' in rules
    assert '/api/students/<int:student_id>/history' in rules

def test_students_requires_auth(client):
    assert client.get('/api/students').status_code == 401
