"""Mentor mentorship / disciplinary structure tests (no live writes)."""

def test_mentor_meetings_and_reports_structure(client):
    rules = [str(x) for x in client.application.url_map.iter_rules()]
    # Mentor decision path shares mentorship-requests; disciplinary reports share help.
    assert '/api/mentorship-requests/<int:req_id>/<decision>' in rules
    assert '/api/help-requests' in rules
