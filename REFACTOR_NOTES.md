# Refactor & Workflow Deliverables — IITM BS Mentoring Portal

## 1. New backend folder structure (implemented)
```
backend/
├── app.py                 # composition root: create_app + error handlers + register_blueprints + run
├── config.py              # typed Config from .env, validates Supabase keys, loads dotenv
├── extensions.py          # Flask app, CORS, single Supabase sb + auth_client
├── .env / .env.example / requirements.txt
├── routes/                # HTTP layer (blueprints)
│   ├── __init__.py        # register_blueprints()
│   ├── auth_routes.py     # /api/auth/*
│   ├── admin_routes.py    # /api/admin/*
│   ├── help_routes.py     # /api/help-requests/*
│   ├── community_routes.py# /api/communities + /api/community-requests
│   ├── mentorship_routes.py
│   ├── mentor_routes.py
│   ├── state_routes.py    # /api/health, /api/state, /api/terms/current
│   ├── meeting_routes.py  # GET+POST /api/meetings
│   ├── notification_routes.py, student_routes.py, search_routes.py
├── services/              # business logic
│   ├── auth_service, state_service, mentor_service, matching_service (cosine),
│   │   ai_service (OpenRouter), mentorship_service, meeting_service,
│   │   help_service, community_service, admin_service, notification_service,
│   │   student_service
├── repositories/          # Supabase data access (best-effort, never crashes request)
│   ├── user, mentor, state, mentorship, help, community, notification _repository.py
├── middleware/            # auth_middleware (login_required, roles), error_handler
├── utils/                 # helpers (state/profile/auth/current_user), responses, validators, constants
├── sql/migrations/001_help_community_approval.sql
└── tests/                 # pytest (17 tests)
```
Note: the live runtime source of truth remains `app_state` payload in Supabase
(Postgres), which the frontend already syncs to. Relational tables in
`sql/migrations/` are written best-effort by repositories and are for the
relational/R audit path once applied.

## 2. Files moved/created
- Created: config.py, extensions.py; routes/* (11), services/* (12),
  repositories/* (7), middleware/* (2), utils/* (4);
  sql/migrations/001_help_community_approval.sql; tests/* (6 + conftest).
- Moved: all handlers from monolithic `app.py` into blueprints; state/profile/
  auth helpers into utils/helpers.py; OpenRouter logic into services/ai_service.py;
  Supabase writes into repositories/*.
- Updated app.py: now 513 bytes — create_app, register_error_handlers,
  register_blueprints, run.

## 3. New API endpoints
Help: POST/GET /api/help-requests, GET /api/help-requests/<id>,
POST /api/help-requests/<id>/messages, PATCH /api/help-requests/<id>/status
(admin), POST /api/help-requests/<id>/assign (admin),
POST /api/help-requests/<id>/interventions (admin),
GET/PATCH /api/admin/help-requests (+ status) same semantics.
Help list filters: ?category=&status=&priority= (and admin date filter in UI).
Statuses: Submitted → Under Review → Additional Information Required →
Approved/Rejected → Resolved → Closed (validated). Priorities: Low/Medium/High/Urgent.
Community requests: POST/GET /api/community-requests, GET /api/community-requests/<id>,
POST /api/community-requests/<id>/approve|reject|request-changes (admin).
Direct POST /api/communities is now admin-only (403 for students/mentors).
GET /api/community-requests is role-aware: admin=all, others=own.

## 4. Frontend changes
- Student/Mentor HelpPage (frontend/src/pages/StudentPages.jsx): role-specific
  categories, priority/urgency, mentor-change fields (current mentor, reason),
  disciplinary fields (student, mentorship, incident category/date, evidence),
  confidentiality banner, tracking filters, admin reply/resolution display,
  additional-info messaging, resolution history.
- Admin HelpTickets (frontend/src/pages/AdminPages.jsx): unified dashboard with
  views (All / Mentor-change approvals / Disciplinary), filters (category/status/
  priority/date), detail view, assign, internal note vs reply, status/decision
  controls, intervention logging, conversation + audit history.
- CommunityPage (frontend/src/pages/CommunityPage.jsx): non-admin sees
  “Request New Community” (purpose, audience, type, reason, moderators,
  supporting info) → POST /community-requests; admin sees approvals panel with
  moderator assignment, approve/reject/request-changes + confirm dialogs;
  requesters track status/rejection_reason/moderation_note.
- App.jsx: sendHelp is now API-backed (POST /help-requests, fallback local
  ticket on failure); Help pages receive updateData for conversation sync.
- Build passes: `npm run build` OK.

## 5. RLS policies (sql/migrations/001_help_community_approval.sql)
Tables: help_requests, help_request_messages, help_request_attachments,
intervention_logs, community_requests, community_request_reviews.
UUID PKs, FKs to user_profiles (set null on delete), enums for status/priority/role,
indices on status/category/priority/date, updated_at triggers.
RLS enabled; service_role_all for backend; authenticated policies:
requester-own or admin select/insert; admin-only update/interventions/reviews.
Storage note: supporting docs → bucket mentoring-files / help-requests/<id>/…

## 6. Test results
- `cd backend && ./.venv/bin/python -m pytest tests -q` → 17 passed.
- Live workflow (/tmp/workflow.py, real Supabase logins):
  1. Student mentor-change submit — PASS (201, persisted in app_state.tickets)
  2. Admin review → Under Review → Additional Info → Approved → Resolved — PASS
  3. Student receives reply/resolution — PASS
  4. Mentor Conduct disciplinary report — PASS (confidential=True)
  5. Admin records intervention — PASS (logged, shown in history)
  6. Student cannot GET mentor confidential ticket (404) nor list it — PASS
  7. Student requests community — PASS (201 Pending, in app_state.community_requests)
  8. Admin approves → community appears in GET /communities — PASS
  9. (covered by 8)
  10. Rejected request shows rejection_reason to requester — PASS
  11. Persistence: GET /api/state shows tickets/community_requests/communities — PASS
  12. /api/auth/me, /api/mentors, /api/mentorship-requests still work — PASS
- Authorization: student direct POST /communities → 403; student approve → 403;
  student PATCH help status → 403; non-admin list scoping → PASS.
- Blueprints: 52 rules, no duplicate endpoint conflicts; frontend `npm run build` OK.

> Workflow verification left test rows (tickets/community requests) in the real
> Supabase app_state. Delete/ignore test entries (# mentor-change, Bad Group XYZ)
> or re-seed app_state if a clean slate is desired.

## 7. Remaining limitations
- `app_state` JSON remains the synchronous source of truth for the SPA
  (frontend PUTs whole state). Relational tables are dual-written best-effort;
  backfilling existing app_state rows into relational tables is not automated.
- Relational migrations must be applied manually in Supabase SQL Editor
  (SQL Editor is the only DDL path in this environment).
- Supporting documents: filename/metadata stored; byte upload to
  mentoring-files bucket is not wired (form accepts files, names persisted).
- Notifications: no dedicated notification inbox table wired to UI events;
  status changes surface by re-fetching tickets/requests. (notification_routes
  exists but UI does not show a bell yet.)

## 8. Exact commands to run
```bash
# Terminal 1 — backend (Flask, port 5001; debug reloader picks up changes)
cd backend
./.venv/bin/python app.py
# health: curl http://localhost:5001/api/health

# Terminal 2 — frontend (Vite, port 5173)
cd frontend
npm run dev -- --host --port 5173
# build check: npm run build

# Tests
cd backend
./.venv/bin/python -m pytest tests -q

# DB (one-time): paste backend/sql/migrations/001_help_community_approval.sql
# into Supabase Dashboard → SQL Editor → Run.

# Demo logins (verified):
#  student@iitm.ac.in / student123  · mentor@iitm.ac.in / mentor123
#  admin@iitm.ac.in   / admin123    · demomentoriitm@iitm.ac.in / mentor123
```

---

# Second-level modular refactor (Nov 9, 2026)

All large files (>~100 lines or multi-responsibility) split by workflow; no endpoint,
method, payload, or auth behavior changed. Largest module now 99 lines (was 249).

## Routes (backend/routes/)
- `auth/register.py` POST register · `auth/login.py` POST login · `auth/session.py` health/me/logout/reset
- `mentor/catalogue.py` list+filter · `mentor/search.py` keyword search · `mentor/indexing.py` AI index
- `mentorship/requests.py` list/create/decide
- `community/discovery.py` list+admin create · `community/creation_requests.py` intake+approve/reject/changes
  · `community/membership.py` join/leave · `community/messages.py` messages/report
- `help/requests.py` student/mentor create/list/read/message · `help/admin_management.py` status/assign/interventions
- `admin/dashboard.py` aggregates · `admin/approvals.py` mentor approve + user status · `admin/help_management.py` /api/admin/help-requests*
- `state/health.py`, `state/terms.py`, `state/lifecycle.py` (state GET/PUT)
- `meeting/meetings.py` list/create · `notification/notifications.py` list/create
- `student/profile.py` roster · `student/history.py` history · `search/mentors.py` search
Each package has `__init__.py` exporting one aggregate blueprint; `routes/__init__.py:register_blueprints()` registers all 11.

## Services (backend/services/)
- `ai/client.py` OpenRouter chat/embedding · `ai/mentor_indexing.py` analyze+vector
- `help/common.py` statuses/ownership · `help/requests.py` user reqs · `help/admin_management.py` decisions/audit
- `community/creation.py` direct create + request · `community/approval.py` approve/reject/changes
  · `community/membership.py` join/leave/visibility · `community/messaging.py` messages/report
- Kept single-responsibility files untouched (no fragmentation):
  `admin_service` (dashboard+approval), `auth_service`, `mentor_service` (catalogue reads),
  `mentorship_service` (term-gated lifecycle), `meeting_service`, `matching_service` (cosine),
  `notification_service`, `state_service`, `student_service`.

## Repositories (backend/repositories/)
One entity per file (already single-responsibility): user, mentor, state, mentorship,
help, community, notification; plus `__init__.py`. All writes best-effort (never crash requests).

## Middleware / Utils
- `middleware/auth_middleware.py` login gate · `middleware/role_middleware.py` role gate · `middleware/error_handler.py` JSON errors
- `utils/term.py` term labels · `utils/state.py` default/get/save app_state · `utils/profile.py` user_profiles read
  · `utils/auth.py` bearer/current_user · `utils/helpers.py` backwards-compat shim re-export
  · `utils/responses|validators|constants.py` unchanged single-purpose.

## Files created / moved / deleted
- Created: 28 new route/service/util/middleware modules + 11 package `__init__.py` files.
- Moved: logic from `community_routes.py` (249) → `community/*`; `auth_routes.py` (195) → `auth/*`;
  `utils/helpers.py` (197) → `utils/term|state|profile|auth.py`; `services/help_service.py` (143) → `services/help/*`;
  `services/ai_service.py` (111) → `services/ai/*` (etc.).
- Deleted: 11 old `routes/*_routes.py` + 3 old flat services (`ai_service`, `help_service`, `community_service`).
  `app.py` still 18 lines; `extensions.py` still the sole Supabase client owner.

## Verification (after refactor)
- `python -m compileall` RC=0 · `import app` → 52 rules (identical to pre-refactor) · no circular imports
- `pytest tests -q` → 17 passed
- Live Flask restart on :5001 + /tmp/workflow.py → all 12 workflows PASS (mentor-change,
  disciplinary confidentiality 404, community approve→discovery, reject reason, persistence, auth)
- Bypass checks: student `POST /communities` 403, approve 403, status PATCH 403
- Frontend: http://localhost:5173/ 200 · `npm run build` OK

---

# Role-based refactor: student / mentor / admin / common (Nov 9, 2026)

Top-level layer folders (`routes/ services/ repositories/ middleware/ utils/`) replaced
by `student/ mentor/ admin/ common/` — verified 52 URLs identical, 27 tests pass,
full workflow re-run green, build green. Supabase stays centralized in `extensions.py`.

Key mapping (canonical URL owner → role services):
- `/api/auth/*` → `common/auth/`; `/api/health|state|terms` → `common/database/`
- `/api/mentors, /filter-options, /search` → `student/mentor_search/`; `/api/mentors/<id>/index` → `admin/matching/`
- `/api/mentorship-requests` → `student/mentorship/` (decide delegates to mentor/admin domains)
- `/api/help-requests` (user) → `student/help/` (mentor help delegates; confidential reports via `mentor/student_reports/`);
  status/assign/interventions → `admin/help_management/` (+ legacy `/api/help-requests/<id>/status|assign|interventions`)
- `/api/communities, /community-requests*` → `common/communities/` (shared infra);
  role services in `student|mentor/communities/`, approvals in `admin/community_approvals/`
- `/api/meetings` → `common/meetings/`; `/api/notifications` → `common/notifications/`
- `/api/admin/dashboard|mentors/<id>/approve|users/<id>/status` → `admin/dashboard|mentor_approvals|users/`
- Frontend→backend coverage: StudentHome/mentor search→student/mentor_search, MyMentorship→student/mentorship,
  MentorRequests/MyStudents→mentor/mentorship+mentees, HelpTickets→admin/help_management,
  CommunityPage→common/communities + role services, Admin dashboard/users→admin/*.

## Commands
```
cd backend && ./.venv/bin/python app.py
cd frontend && npm run dev -- --host --port 5173
cd backend && ./.venv/bin/python -m pytest tests -q
```

---

# AI Mentor Matching & RAG Audit + Implementation (Nov 9, 2026)

## Audit (pre-fix state)
- LLM analysis + embedding generation existed in `common/ai/client.py` (OpenRouter
  `openrouter/free` chat + `text-embedding-3-small` 1536-dim) and
  `common/ai/mentor_indexing.py` (writes `vector`+`ai_profile` to app_state, best-effort
  `mentor_vectors` upsert).
- BUT: approval (`admin/mentor_approvals/service.approve_mentor`) did NOT trigger indexing
  (separate POST /api/mentors/<id>/index only); `mentor_profiles`/`mentor_vectors`
  tables do not exist in live Supabase (PGRST205), so pgvector path was dead code.
- Student search (`student/mentor_search/service.keyword_search`) was keyword-only with
  hardcoded `score=0.85`, `embedding_search=False`, ignored the query text, no
  eligibility/capacity filters, no vector use (`common/ai/matching.cosine_similarity`
  existed but unused), raw vectors leaked to clients.
- Frontend `RecommendationChat` called `/mentors/search` but only showed names;
  the local `getMatches()` keyword fallback duplicated backend logic.

## Implementation (RAG fix, no mocks)
- `common/ai/embeddings.py` (query embedding, profile serialization, 1536-dim constants)
- `common/ai/vector_store.py` (pgvector RPC `match_mentors` with cosine fallback over
  precomputed app_state vectors; best-effort search audit log)
- `common/ai/retrieval.py` (`semantic_search`: embed query once, eligibility+capacity
  gates, manual filters, cosine/pgvector ranking, ai_profile-grounded `reason`)
- `admin/mentor_approvals/service.approve_mentor` now auto-analyzes+embeds on approval
  (best-effort; approval never blocked). `admin/matching/service.ensure_indexed` precomputes once.
- `student/mentor_search/service+routes` serve top-5 ranked results, strip vectors,
  `search_method` ∈ {pgvector, cosine, keyword}.
- `student/mentorship/service+routes` persist `preferences` (selected mentors) with
  goal/message; frontend `App.createRequest` calls POST /mentorship-requests;
  `RecommendationChat`/`MentorDetails` render explanation + score.
- `backend/sql/migrations/002_rag_vector_index.sql` creates `mentor_profiles`,
  `mentor_vectors (vector(1536))`, `mentor_search_logs`, ivfflat index, `match_mentors()` RPC.

## Live results (real Supabase + OpenRouter)
- `machine learning` → Meera Shah (0.49, ML skills/topics cited) top-1
- `product analytics` → Arjun Nair (0.48) top-1
- `starting a company` → Rohan Das (0.53) top-1
- `embedding_search=True`, `search_method=cosine` (pgvector tables absent → cosine path),
  no vector leak, re-index idempotent, formal request with preferences persisted.

---

# Conversational AI Career Assistant + `/find` RAG (Nov 9, 2026)

## Backend (`common/ai/`, `student/mentor_search/`)
- `common/ai/intent_router.py` — `/find` detection (boundary-aware, empty→clarification)
- `common/ai/chat_service.py` — general career chat via OpenRouter text (greetings/concepts/
  roadmaps/interview, 8-turn history, deterministic small-talk, no vector search)
- `common/ai/query_enhancer.py` — LLM extraction of skills/expertise/industry/role/goals/
  mentoring_requirements + enhanced_query shown to the student (regex fallback)
- `common/ai/mentor_rag.py` — `/find` orchestrator: enhance → embed once → RAG top-5 +
  `top_explanation` grounded strictly in retrieved `ai_profile`/bio (real cosine scores)
- `student/mentor_search/chat.py` — `POST /api/mentors/chat {message,history}` router
  (mode=find|chat|clarification|error); `POST /api/mentors/search` kept for back-compat.
- `common/ai/client.py` — added shared `_post_chat()` + `openrouter_text()` (no duplicate clients).
- Fixed index persistence bug (`save_state(get_state())` discarded mutations → now saves same object)
  and added `PUT /state` vector guard so frontend syncs never wipe precomputed vectors.

## Frontend (`RecommendationChat.jsx`)
- `/find` suggestions + placeholder, enhancement/loading phases, chat vs. recommendation
  separation, featured #1 card + “Why ranked first” panel, history preserved,
  empty/error states. General messages go to chat; only `/find` triggers search.

## Verified live (student@iitm.ac.in)
- Hi / deep-learning / ML-roadmap / interview-with-history → chat mode, no mentors, no vectors
- `/find` (empty) → clarification prompt; `/find ML engineer mentor` → enhanced query +
  4 distinct eligible matches, Meera top (0.40), grounded explanation, no vector leak
- `/find Python/data-science` → Arjun top; over-5 capped at 5; restrictive filter → 0 with
  “no eligible mentors” message; fewer-than-5 returns 4 (only 4 approved mentors exist)
- `pytest` 29 passed; rules 53 (+/chat); `npm run build` OK.

---

# Production UI polish — hide AI internals (Nov 9, 2026)

- Backend `common/ai/retrieval.py:build_reason` + `mentor_rag.top_explanation` rewritten to
  friendly natural language (no "Matched via cosine", no scores, no "semantic similarity
  over precomputed profile vectors"); `semantic_search` strips `_score/method/embedding`
  from the API surface; `/find` replies are "We found N relevant mentors." with profile-grounded
  first-place story. Enhanced queries, extracted dimensions, embeddings, scores and prompts
  are backend-only (still used internally for ranking).
- Frontend `RecommendationChat.jsx`: no enhanced-query echo, no Similarity/Score UI,
  cards show name / role / expertise / concise reason / View Profile, featured top match
  with natural story, "Finding mentors that fit your goals…" loading, honest counts (N=1 singular).
- Verified: Hi / deep-learning / ML-roadmap / interview-history → chat (no mentors);
  `/find` empty → clarification; `/find ML engineer mentor` → enhanced internally only,
  4 distinct eligible matches (fewer-than-5 phrasing), top explanation natural, zero leaks
  (enhanced/scores/methods/vectors absent from payloads); `pytest` 29 passed; build OK.
