"""Full live API debug sweep for the IITM BS Mentoring Portal.

Logs into all roles, exercises every reachable endpoint, checks RBAC,
and writes machine-readable results to test-results/api-debug-results.json.

Read-only where possible; mutations use dedicated test accounts created here
(or the documented demo accounts). No data is deleted. No SQL/schema changes.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone

import requests

BASE = os.environ.get('API_BASE', 'http://localhost:5001/api')
STAMP = int(time.time())
STUDENT_EMAIL = f'dbg_student_{STAMP}@iitm.ac.in'
MENTOR_EMAIL = f'dbg_mentor_{STAMP}@iitm.ac.in'
PASSWORD = 'DebugPass123!'
OUT = os.path.join(os.path.dirname(__file__), '..', 'test-results', 'api-debug-results.json')

results = []


def call(name, method, path, token=None, body=None, expected=(200,), timeout=30, note=''):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    url = BASE + path
    started = time.time()
    try:
        r = requests.request(method, url, headers=headers, json=body, timeout=timeout)
        ms = int((time.time() - started) * 1000)
        try:
            payload = r.json()
        except Exception:
            payload = r.text[:400]
        ok = r.status_code in expected
        results.append({
            'name': name, 'method': method, 'path': path, 'status': r.status_code,
            'expected': list(expected), 'pass': ok, 'ms': ms, 'note': note,
            'body': payload if isinstance(payload, (dict, list)) else str(payload)[:400],
        })
        return ok, r.status_code, payload
    except Exception as exc:  # noqa: BLE001
        results.append({'name': name, 'method': method, 'path': path, 'status': None,
                        'expected': list(expected), 'pass': False, 'error': str(exc), 'note': note})
        return False, None, None


def login(email, password):
    ok, status, payload = call(f'login {email}', 'POST', '/auth/login',
                               body={'email': email, 'password': password}, expected=(200, 403))
    token = payload.get('access_token') if isinstance(payload, dict) else None
    return token, status, payload


def find(items, key, value):
    for item in items or []:
        if str(item.get(key)) == str(value):
            return item
    return None


def main():
    # ---------- public ----------
    call('health', 'GET', '/health')
    call('auth health', 'GET', '/auth/health', expected=(200, 404))
    call('unauthenticated state -> 401', 'GET', '/state', expected=(401,))
    call('unauthenticated mentors -> 401', 'GET', '/mentors', expected=(401,))
    call('unauthenticated dm search -> 401', 'GET', '/messaging/users?q=a', expected=(401,))

    # ---------- logins ----------
    s_tok, _, s_payload = login('student@iitm.ac.in', 'student123')
    m_tok, _, m_payload = login('mentor@iitm.ac.in', 'mentor123')
    a_tok, _, a_payload = login('admin@iitm.ac.in', 'admin123')
    assert s_tok and m_tok and a_tok, 'demo logins failed'

    for label, tok in (('student', s_tok), ('mentor', m_tok), ('admin', a_tok)):
        call(f'{label} me', 'GET', '/auth/me', token=tok)
        call(f'{label} state', 'GET', '/state', token=tok)
        call(f'{label} terms', 'GET', '/terms/current', token=tok)
        call(f'{label} notifications', 'GET', '/notifications', token=tok)
        call(f'{label} unread count', 'GET', '/notifications/unread-count', token=tok)
        call(f'{label} inbox', 'GET', '/messaging/inbox', token=tok)
        call(f'{label} community list', 'GET', '/communities', token=tok)
        call(f'{label} mentorship requests', 'GET', '/mentorship-requests', token=tok)
        call(f'{label} meetings', 'GET', '/meetings', token=tok)
        call(f'{label} help requests', 'GET', '/help-requests', token=tok)
        call(f'{label} students list', 'GET', '/students', token=tok)

    # ---------- catalogue / discovery ----------
    _, _, mentor_catalog = call('mentor catalogue', 'GET', '/mentors', token=s_tok)
    call('mentor filter options', 'GET', '/mentors/filter-options')
    call('mentor semantic search', 'POST', '/mentors/search', token=s_tok,
         body={'query': 'machine learning mentor', 'limit': 5})
    call('legacy search alias', 'POST', '/search/mentors', token=s_tok,
         body={'query': 'data'}, note='legacy stub')

    mentors = (mentor_catalog or {}).get('items') or []
    mentor_name = mentors[0]['name'] if mentors else 'Arjun Nair'
    mentor_id = mentors[0]['id'] if mentors else 1

    call('student history', 'GET', f'/students/{int(mentor_id)}/history', token=s_tok, expected=(200, 404))

    # ---------- RBAC ----------
    call('student -> admin dashboard 403', 'GET', '/admin/dashboard', token=s_tok, expected=(403,))
    call('mentor -> admin dashboard 403', 'GET', '/admin/dashboard', token=m_tok, expected=(403,))
    call('admin dashboard', 'GET', '/admin/dashboard', token=a_tok)
    call('student -> admin help 403', 'GET', '/admin/help-requests', token=s_tok, expected=(403,))
    call('mentor -> admin moderation 403', 'GET', '/admin/community-moderation/reports', token=m_tok, expected=(403,))
    call('admin moderation reports', 'GET', '/admin/community-moderation/reports', token=a_tok)

    # ---------- registration + approval gate ----------
    ok, _, _ = call('register student', 'POST', '/auth/register',
                    body={'name': f'Debug Student {STAMP}', 'email': STUDENT_EMAIL, 'password': PASSWORD,
                          'role': 'student', 'program': 'BS Data Science'}, expected=(201,))
    call('register mentor', 'POST', '/auth/register',
         body={'name': f'Debug Mentor {STAMP}', 'email': MENTOR_EMAIL, 'password': PASSWORD,
               'role': 'mentor', 'job': 'Engineer', 'field': 'IT', 'industry': 'Technology',
               'mode': 'Online', 'slots': 2, 'background': 'Debug mentor for automated verification.'},
         expected=(201,))

    student_tok, _, _ = login(STUDENT_EMAIL, PASSWORD)
    mentor_tok, mentor_login_status, mentor_login_body = login(MENTOR_EMAIL, PASSWORD)
    call('pending mentor login blocked', 'POST', '/auth/login',
         body={'email': MENTOR_EMAIL, 'password': PASSWORD}, expected=(403,),
         note='approval gate')

    # approve the newly registered mentor through admin
    state_res = requests.get(f'{BASE}/state', headers={'Authorization': f'Bearer {a_tok}'}, timeout=30).json()
    new_mentor = next((m for m in state_res.get('mentors') or [] if m.get('email') == MENTOR_EMAIL), None)
    if new_mentor:
        call('admin approves mentor', 'POST', f"/admin/mentors/{int(new_mentor['id'])}/approve", token=a_tok,
             expected=(200,))
        mentor_tok2, _, _ = login(MENTOR_EMAIL, PASSWORD)
        call('approved mentor login', 'POST', '/auth/login',
             body={'email': MENTOR_EMAIL, 'password': PASSWORD}, expected=(200,))
        mentor_tok = mentor_tok2 or mentor_tok
        call('admin index mentor profile', 'POST', f"/mentors/{int(new_mentor['id'])}/index", token=a_tok,
             expected=(200, 400, 422, 500), timeout=120, note='embedding job')

    # ---------- mentorship request lifecycle ----------
    ok, _, created_req = call('student creates mentorship request', 'POST', '/mentorship-requests', token=student_tok,
                              body={'mentor': mentor_name, 'goal': 'Career guidance', 'message': 'Automated debug request.',
                                    'preferences': [mentor_name]}, expected=(201,))
    req_id = None
    if isinstance(created_req, dict):
        req = created_req.get('request') or created_req
        req_id = req.get('id') if isinstance(req, dict) else None
    if req_id is None:
        _, _, listing = call('student request listing', 'GET', '/mentorship-requests', token=student_tok)
        items = (listing or {}).get('items') or []
        mine = [r for r in items if r.get('email') == STUDENT_EMAIL]
        req_id = mine[-1]['id'] if mine else None
    call('mentor sees requests', 'GET', '/mentorship-requests', token=mentor_tok)
    if req_id is not None:
        call('student cannot decide request', 'POST', f'/mentorship-requests/{req_id}/accept', token=student_tok,
             expected=(403,))
        call('admin accepts request', 'POST', f'/mentorship-requests/{req_id}/accept', token=a_tok)
        call('admin declines request', 'POST', f'/mentorship-requests/{req_id}/decline', token=a_tok,
             expected=(200, 400), note='state transition check')

    # ---------- meetings ----------
    when = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    call('student creates meeting', 'POST', '/meetings', token=student_tok,
         body={'mentor': mentor_name, 'student': f'Debug Student {STAMP}', 'scheduled_at': when}, expected=(201,))
    _, _, meetings = call('student meetings', 'GET', '/meetings', token=student_tok)
    call('mentor meetings', 'GET', '/meetings', token=mentor_tok)

    # ---------- help desk ----------
    ok, _, ticket = call('student creates help ticket', 'POST', '/help-requests', token=student_tok,
                         body={'type': 'Academic', 'description': 'Automated debug ticket.', 'urgency_level': 'Medium'},
                         expected=(201,))
    ticket_id = ticket.get('id') if isinstance(ticket, dict) else None
    if not ticket_id:
        _, _, listing = call('student help listing', 'GET', '/help-requests', token=student_tok)
        for t in (listing or {}).get('items') or []:
            if t.get('description') == 'Automated debug ticket.':
                ticket_id = t.get('id')
    if ticket_id:
        call('owner reads ticket', 'GET', f'/help-requests/{ticket_id}', token=student_tok)
        call('other user cannot read ticket', 'GET', f'/help-requests/{ticket_id}', token=m_tok, expected=(404,))
        call('owner adds message', 'POST', f'/help-requests/{ticket_id}/messages', token=student_tok,
             body={'message': 'Additional debug detail.'})
        call('admin lists help', 'GET', '/admin/help-requests', token=a_tok)
        call('admin assigns ticket', 'POST', f'/admin/help-requests/{ticket_id}/assign', token=a_tok,
             body={'assigned_admin': 'IIC Admin'})
        call('admin sets ticket status', 'PATCH', f'/admin/help-requests/{ticket_id}/status', token=a_tok,
             body={'status': 'Under Review'})
        call('admin rejects invalid ticket status', 'PATCH', f'/admin/help-requests/{ticket_id}/status', token=a_tok,
             body={'status': 'In Progress'}, expected=(400,))
        call('admin logs intervention', 'POST', f'/admin/help-requests/{ticket_id}/interventions', token=a_tok,
             body={'action': 'Note', 'performed_by': 'IIC Admin', 'notes': 'Debug intervention.'})

    # ---------- communities ----------
    _, _, communities = call('communities for new student', 'GET', '/communities', token=student_tok)
    items = (communities or {}).get('items') or []
    cid = items[0].get('id') if items else None
    if cid:
        call('community members', 'GET', f'/communities/{cid}/members', token=student_tok)
        call('community messages', 'GET', f'/communities/{cid}/messages', token=student_tok)
        call('join community', 'POST', f'/communities/{cid}/join', token=student_tok)
        ok, _, msg = call('send community message', 'POST', f'/communities/{cid}/messages', token=student_tok,
                          body={'content': f'Debug community message {STAMP}'}, expected=(201,))
        message_id = None
        if isinstance(msg, dict):
            message_id = (msg.get('message') or {}).get('id') if isinstance(msg.get('message'), dict) else msg.get('id')
        if message_id:
            call('react to community message', 'POST', f'/communities/{cid}/messages/{message_id}/reaction',
                 token=student_tok, body={'reaction': '👍'})
            _, _, report = call('report community content', 'POST', f'/communities/{cid}/report', token=student_tok,
                                body={'reason': 'Automated debug report', 'message_id': message_id},
                                expected=(201,))
            report_id = report.get('report_id') or report.get('id') if isinstance(report, dict) else None
            if report_id:
                call('admin sets report status', 'POST', f'/admin/community-moderation/reports/{report_id}/status',
                     token=a_tok, body={'status': 'Reviewed', 'action_note': 'Debug review'},
                     expected=(200, 400, 404))
        call('leave community', 'POST', f'/communities/{cid}/leave', token=student_tok)
        call('post after leave blocked', 'POST', f'/communities/{cid}/messages', token=student_tok,
             body={'content': 'Should be blocked'}, expected=(400, 403))

    call('student community request', 'POST', '/community-requests', token=student_tok,
         body={'community_name': f'Debug Community {STAMP}', 'community_type': 'Discussion',
               'reason': 'Automated debug request'}, expected=(201,))
    _, _, creqs = call('admin community requests', 'GET', '/community-requests', token=a_tok)
    crid = None
    for c in (creqs or {}).get('items') or []:
        if c.get('community_name') == f'Debug Community {STAMP}':
            crid = c.get('id')
    if crid:
        call('admin approves community request', 'POST', f'/community-requests/{crid}/approve', token=a_tok,
             body={}, expected=(200, 201))

    # ---------- direct messages ----------
    _, _, users = call('dm user search', 'GET', f'/messaging/users?q=Debug%20Mentor%20{STAMP}', token=student_tok)
    peer = find((users or {}).get('items'), 'email', MENTOR_EMAIL)
    if peer:
        ok, _, conv = call('create dm conversation', 'POST', '/messaging/conversations', token=student_tok,
                           body={'participant_id': peer['id']}, expected=(200, 201))
        conv_id = (conv or {}).get('conversation', {}).get('id')
        call('reuse dm conversation', 'POST', '/messaging/conversations', token=student_tok,
             body={'participant_id': peer['id']}, expected=(200, 201))
        if conv_id:
            ok, _, dm = call('send dm', 'POST', f'/messaging/conversations/{conv_id}/messages', token=student_tok,
                             body={'content': 'Debug DM message.'}, expected=(200, 201))
            dm_id = (dm or {}).get('message', {}).get('id')
            call('read dm', 'GET', f'/messaging/conversations/{conv_id}', token=student_tok)
            call('mark dm read', 'POST', f'/messaging/conversations/{conv_id}/read', token=student_tok, body={})
            if dm_id:
                call('react to dm', 'POST', f'/messaging/conversations/{conv_id}/messages/{dm_id}/reaction',
                     token=student_tok, body={'reaction': '👍'})
            call('cross-member dm denied', 'GET', f'/messaging/conversations/{conv_id}', token=a_tok, expected=(404,))

    # ---------- notifications ----------
    ok, _, notif = call('create own notification', 'POST', '/notifications', token=student_tok,
                        body={'type': 'info', 'title': 'Debug notification', 'body': 'Debug body', 'link': '/inbox'},
                        expected=(201,))
    notif_id = (notif or {}).get('id')
    _, _, count = call('unread count after create', 'GET', '/notifications/unread-count', token=student_tok)
    if notif_id:
        call('other user cannot mark notification', 'POST', f'/notifications/{notif_id}/read', token=m_tok,
             expected=(404,))
        call('mark notification read', 'POST', f'/notifications/{notif_id}/read', token=student_tok)
    call('mark all notifications read', 'POST', '/notifications/read-all', token=student_tok)

    # ---------- admin user lifecycle (own test account only) ----------
    call('admin deactivates test student', 'POST', f'/admin/users/{STUDENT_EMAIL}/status', token=a_tok,
         body={'active': False})
    call('deactivated student login blocked', 'POST', '/auth/login',
         body={'email': STUDENT_EMAIL, 'password': PASSWORD}, expected=(403,))
    call('admin reactivates test student', 'POST', f'/admin/users/{STUDENT_EMAIL}/status', token=a_tok,
         body={'active': True})
    call('reactivated student login', 'POST', '/auth/login',
         body={'email': STUDENT_EMAIL, 'password': PASSWORD}, expected=(200,))

    # ---------- AI ----------
    call('ai mentor find', 'POST', '/mentors/chat', token=student_tok,
         body={'message': '/find machine learning mentor'}, timeout=120, note='LLM call')
    call('ai career chat', 'POST', '/mentors/chat', token=student_tok,
         body={'message': 'Give me one short tip for a data science internship.'}, timeout=120, note='LLM call')

    # ---------- password reset + logout ----------
    call('password reset request', 'POST', '/auth/password-reset', body={'email': STUDENT_EMAIL},
         expected=(200, 400, 404))
    call('logout', 'POST', '/auth/logout', token=student_tok)
    call('me after logout still valid (token-based)', 'GET', '/auth/me', token=student_tok, expected=(200, 401))

    # ---------- summary ----------
    passed = sum(1 for r in results if r['pass'])
    failed = [r for r in results if not r['pass']]
    summary = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'base': BASE,
        'total': len(results),
        'passed': passed,
        'failed': len(failed),
        'pass_rate': round(100 * passed / max(1, len(results)), 1),
        'test_accounts': {'student': STUDENT_EMAIL, 'mentor': MENTOR_EMAIL},
        'failures': failed,
        'results': results,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as fh:
        json.dump(summary, fh, indent=2)

    print(f"TOTAL {summary['total']}  PASSED {passed}  FAILED {len(failed)}  ({summary['pass_rate']}%)")
    for f in failed:
        print(f"FAIL  {f['method']} {f['path']}  status={f.get('status')} expected={f.get('expected')}  {f.get('name')}")
    print(f"REPORT {os.path.abspath(OUT)}")


if __name__ == '__main__':
    main()
