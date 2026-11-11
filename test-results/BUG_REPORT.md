# E2E Bug Report

## B1 (P1) — Community chat never enables after joining
**Role:** Student/Mentor · **Steps:** Communities → click “+ Join” (or “Join Community”) → input stays disabled (“Join to participate…”).
**Expected:** Chat input enables with “Write a message…”.
**Actual:** Only the browse-card list toggled; `activeCommunity` stayed stale, so the input never enabled until the card was re-selected.
**Root cause:** `handleJoinLeave` updated `communities` but not `activeCommunity`.
**Fix:** `frontend/src/pages/CommunityPage.jsx` — added `syncMembership()` updating both lists + panel. **Retest:** Join FinTech → input enabled → message appears. **File:** `CommunityPage.jsx`
**STATUS:** ✅ RESOLVED & VERIFIED

## B2 (P1) — Approvals button never unlocked mentor login
**Role:** Admin · **Steps:** Approve a pending mentor in the UI → mentor still cannot log in.
**Root cause 1:** `Approvals` only mutated local `data` (synced via whole-state `PUT /state`); it never called `POST /api/admin/mentors/<id>/approve`.
**Root cause 2:** `admin/mentor_approvals/service.approve_mentor` never updated `user_profiles` (login gate reads that table): state `approved=true`, profile `approved=false` (verified: QA Mentor `1794244741`).
**Fix:** UI now calls the backend approve/status endpoints; services sync `user_profiles.approved/active`. **Retest:** Fresh mentor registered in browser → admin Approve → `user_profiles.approved=true` → login succeeds → appears in student discovery. **Files:** `AdminPages.jsx`, `admin/mentor_approvals/service.py`, `admin/users/service.py`
**STATUS:** ✅ RESOLVED & VERIFIED

## B3 (P2) — Mentor modal stayed open across navigation
**Role:** Student · **Steps:** Open View Profile → click nav → modal still rendered over new page.
**Fix:** Nav click also clears `selectedMentor` (`App.jsx`). **STATUS:** ✅ RESOLVED
**Files:** `App.jsx`

## B4 (P2) — Scheduled meetings lost their date
**Role:** Student · **Steps:** Schedule meeting → API shows `scheduled_at: null`.
**Root cause:** Frontend wrote `{student, mentor, date}`; backend reads `scheduled_at` (schema mismatch).
**Fix:** Frontend writes both keys; backend `GET /api/meetings` normalizes legacy `date` → `scheduled_at`. **Retest:** Meeting persists with `2026-11-20T18:00`. **STATUS:** ✅ RESOLVED & VERIFIED
**Files:** `StudentPages.jsx`, `common/meetings/routes.py`

## B5 (P2) — Disciplinary reports not flagged confidential
**Role:** Mentor · **Steps:** Submit "Student disciplinary…" report → no Confidential banner/flag.
**Root cause:** Detection used exact-match on `ticket_type`; rich type names never matched.
**Fix:** Substring match on `conduct/disciplinary/misconduct/inappropriate` (`student/help/routes.py`). **STATUS:** ✅ RESOLVED & VERIFIED
**Files:** `student/help/routes.py`

## B6 (P2) — Inbox DM conversation detail missing peer context
**Role:** Student · **Steps:** Open Inbox → open a DM conversation → chat header fell back to generic label; read-receipt context incomplete.
**Root cause:** `GET /api/messaging/conversations/<uuid>` service returned conversation/participant/messages but not the resolved `other` peer (name/role/last-read).
**Fix:** `backend/common/messaging/service.py` `get_conversation` now resolves and returns the `other` peer block. **Retest:** Backend suite + frontend build + browser Inbox render → fixed. **STATUS:** ✅ RESOLVED
**Files:** `backend/common/messaging/service.py`, `frontend/src/pages/InboxPage.jsx`

## B7 (P2) — Notifications silently failed to persist (wrong column name)
**Role:** All · **Steps:** Trigger a notification (e.g., DM send) → check `notifications` table.
**Root cause:** Service inserted `body` while the schema column is `message`; exception was swallowed → zero notifications ever stored.
**Fix:** `common/notifications/service.py` now writes `message` (plus `link`/`payload` support). **Retest:** `POST /api/messaging/.../messages` path inserts via fixed writer; suite green. **STATUS:** ✅ RESOLVED & VERIFIED
**Files:** `backend/common/notifications/service.py`

## B8 (P2) — Admin community-moderation blueprint URL prefix doubled
**Role:** Admin · **Steps:** Call `GET /api/admin/community-moderation/reports`.
**Root cause:** Sub-blueprint registered on `admin_bp` (prefix `/api/admin`) already carrying `/api/admin/community-moderation` prefix → effective path doubled.
**Fix:** Sub-blueprint `url_prefix` set to `/community-moderation`. **Retest:** Route registration check passes; live unauth call → `401`. **STATUS:** ✅ RESOLVED & VERIFIED
**Files:** `backend/admin/community_moderation/routes.py`, `backend/admin/routes.py`

## Notes (not bugs)
- Admin community queue timing: the empty queue observed mid-run was a read-before-fetch race (fetch resolves ~async); after wait, the queue renders correctly.
- Chat input appearing “stuck” after `/find` was a test-harness double-submit + React value-tracker artifact; manual clear verifies `setText('')` works.
- Backend was down at session start (connection refused on :5001); restarted via `backend/.venv/bin/python app.py` → `/api/health` → `200 OK`.
