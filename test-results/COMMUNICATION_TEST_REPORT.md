# Communication Platform Test Report — IITM BS Mentoring Portal

**Scope:** Community Chat · Direct Messaging (DM) · Unified Inbox · Notifications · Realtime/Polling ·
Moderation · Attachments/Replies/Reactions · Responsive Inbox.

**Phase:** Build + verify of the Communication Platform layer (migrations, backend messaging APIs,
notifications, community chat upgrades, Inbox UI).

**Date:** 2026-11-11

## 1. Summary (terminal)

```text
========================================
 IITM BS MENTORING PORTAL – COMM. PLATFORM TEST
========================================
Migration 003 (conversations/DMs/reads/RLS) : PARTIAL (SQL file written; SQL Editor apply pending)
Backend messaging routes                              : PASS (registered + auth-guarded)
Notifications endpoints + writer fix                : PASS (writer fix verified in code)
Community reactions/replies/members                : PASS (routes + tests)
Admin moderation endpoints                          : PASS (routes + tests)
Backend full suite                                   : PASS (47 passed, 1 skipped)
New messaging tests                                  : PASS (3 passed)
Frontend production build                            : PASS
Live API smoke (unauth 401 / invalid-uuid 404)       : PASS
Browser (real session restore + Inbox nav render) : PASS
========================================
```

## 2. Phase Status

| Phase | Deliverable | Status |
|---|---|---|
| 1. Inspect + design SQL schema | `backend/supabase_setup.sql`, migrations 001–003 | ✅ Design complete; 003 written (apply pending) |
| 2. Shared backend messaging services | `common/messaging/*`, repos | ✅ Implemented + tested |
| 3. DM APIs + persistence | conversations/participants/DMs/read | ✅ Implemented; live write-path E2E pending (opt-in per safety) |
| 4. Inbox UI + history | `frontend/src/pages/InboxPage.jsx` | ✅ Built + browser-verified render |
| 5. Community chat upgrade | reactions/replies/members/moderation | ✅ Backend + frontend wired |
| 6. Notifications + unread | endpoints + writer fix + DM trigger | ✅ Implemented + tested |
| 7. Realtime | polling fallback (15s inbox / 20s notif) | ✅ Implemented (Supabase Realtime deferred — custom JWT auth) |
| 8. Reactions/replies/attachments/moderation/responsive | ✅ Backend+UI; attachments metadata-only | ✅ Backend; UI file-attach pending |
| 9. E2E across roles | see §4 | 🔄 In progress |

## 3. Delivered features (this phase)

1. `conversations`, `conversation_participants`, `direct_messages`, `message_reads` (+ indexes/RLS) via
   `backend/sql/migrations/003_communication.sql`.
2. `notifications.link` / `notifications.payload` columns; writer column fix (`message`).
3. Backend: `GET/POST /api/messaging/inbox`, `POST /api/messaging/conversations`,
   `GET /api/messaging/conversations/<uuid>`, `POST /api/messaging/conversations/<uuid>/messages`,
   `POST /api/messaging/conversations/<uuid>/read`,
   `POST /api/messaging/conversations/<uuid>/messages/<uuid>/reaction`,
   `GET /api/messaging/users` (search).
4. Backend: notification read endpoints (`/read`, `/read-all`, `/unread-count`) + DM-send notification trigger.
5. Backend: community reactions (`POST /api/communities/<cid>/messages/<mid>/reaction`),
   replies (`reply_to_id` on `POST /api/communities/<cid>/messages`), member list (`GET /api/communities/<cid>/members`).
6. Backend: admin moderation (`/api/admin/community-moderation/reports`,
   `.../reports/<uuid>/status`, `.../messages/<int>/delete`).
7. Frontend: Inbox page (conversation list + chat window, search, unread badges, reply, reactions, send,
   mark-read, polling fallback, mobile full-screen chat), Inbox nav item for student/mentor/admin,
   notifications bell + dropdown (mark read / mark all / unread badge / deep-link navigation).
8. Frontend: Message buttons on MentorDetails + StudentProfile + community member rows (DM deep-link flow).

## 4. Test results (this phase)

- Backend: `pytest tests -q` → **47 passed, 1 skipped** (new: `tests/common/test_messaging.py` 3 passed).
- Route registration assertions → all new endpoints present; unauth access → 401; invalid uuid → 404.
- Frontend: `npm run build` → **OK** (Tailwind/React production build).
- Live: `GET /api/health` → 200; new endpoints unauth → 401; invalid uuid → 404.
- Browser: real session restore (token → `apiMe` → Home), Inbox nav click → page heading `Inbox` rendered,
  notifications bell present. Screenshot capture unavailable in current session (browser window visibility).

## 5. Bugs found & fixed during this phase (added to BUG_REPORT.md)

- B6 (P2) Inbox DM peer resolution — fixed (service now returns `other`).
- B7 (P2) Notifications writer column mismatch (`body`→`message`) — fixed & verified.
- B8 (P2) Admin moderation blueprint prefix doubling — fixed & verified.

## 6. Remaining limitations / pending ops

- Migration `003_communication.sql` not yet executed against the live Supabase project (SQL Editor pending).
- Full live DM write/read E2E (create conversation → send → read → unread → reaction) requires opt-in
  live-write mode (existing E2E policy); backend write path code + tests are in place.
- Attachments: backend accepts/validates metadata; frontend file-picker UI pending.
- Typing indicators/online status: backend has no presence model → polling fallback only (documented).
- Supabase Realtime: deferred (custom Flask JWT auth; polling fallback implemented).

## 7. Deliverables

- `backend/sql/migrations/003_communication.sql`
- `backend/common/messaging/{__init__,routes,service}.py`
- `backend/common/database/repos/messaging_repository.py`
- `backend/common/notifications/{service,routes}.py`
- `backend/admin/community_moderation/{__init__,service,routes}.py`
- `backend/tests/common/test_messaging.py`
- `frontend/src/pages/InboxPage.jsx`
- `frontend/src/api.js` (messaging + notification helpers)
- `frontend/src/App.jsx`, `frontend/src/data.js`, `frontend/src/pages/CommunityPage.jsx`, `frontend/src/pages/StudentPages.jsx`
- `API_DOCUMENTATION.md`, `DATABASE_DOCUMENTATION.md`
- `test-results/COMMUNICATION_TEST_REPORT.md` (this file), `test-results/BUG_REPORT.md`, `test-results/screenshots/`, `test-results/test-execution.log`

## 8. Round 2 — Community Chat UX + DM-from-Message (2026-11-11)

### Changes delivered in Round 2

1. **Members section removed** from the community chat view.
   - Removed the standalone Members panel that rendered above the chat (state, loader, JSX).
   - Chat now occupies the full content column → more space for conversation.
   - **Preserved:** community name, description, member count display, Join/Leave (backend membership untouched).

2. **Start DM from a community message.**
   - Sender name and avatar are now clickable → opens small profile popup (`senderProfile`).
   - Popup shows sender name, role badge, context and a **Message** button.
   - `messageSender` resolves sender via `onMessage({ name, role })` → App `startDm` → user search → find-or-create DM → open in Inbox.

3. **Inbox integration.**
   - `App.startDm` → `apiCreateConversation` → `inboxFocusId` → `InboxPage` auto-opens the conversation (`focusConversationId` effect → `openConversation` → mark-read).
   - Existing conversations are reused (backend find-or-create); history loaded from `GET /api/messaging/conversations/<uuid>`.

4. **Security posture (verified in code + existing tests).**
   - Sender identity (name/role/content) sourced from backend-persisted community messages.
   - Community messages and DMs use separate data stores/tables — no DM history leakage into community views.
   - DM send/read/reaction enforce conversation-participant authorization (backend tests + live 401 smoke).

### Round 2 test status

- `npm run build` → **OK** (after Members removal + sender-click wiring).
- Backend suite → **47 passed, 1 skipped** (unchanged, green).
- Live: backend `:5001` running; `/api/health` → 200; unauth new endpoints → 401; invalid UUID → 404.

### Round 2 outstanding manual checks (browser, per user instruction)

- Click sender name/avatar → popup → **Message** → Inbox opens/creates DM → send → reopen → history preserved.
- Verify other community members cannot access the private DM (participant-only backend enforcement + 401/403 behavior).
- Full click-through pending live-DB migration apply (`003_communication.sql`) for write-path E2E.
