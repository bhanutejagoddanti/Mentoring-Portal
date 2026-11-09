# IITM BS Mentoring Portal – Feature Implementation Matrix

Source: inspection of `frontend/src/**` and `backend/app.py` + `backend/supabase_setup.sql`.

Legend for **Implementation Status**:
- **Implemented** – code path complete end-to-end (UI ↔ API ↔ DB where applicable).
- **Partially implemented** – core path exists but with prototype/local-state fallbacks or incomplete data.
- **UI only** – UI exists; logic/persistence local (frontend state) only.
- **Backend only** – API/DB exist; no UI wiring.
- **Planned** – schema/endpoint designed but flow not built.
- **Missing** – neither UI nor backend flow exists.
- **Not verified** – identified but not executed/inspected.

---

## 1. Feature Matrix

| Module | Feature | Student | Mentor | Admin | Status |
|---|---|---|---|---|---|
| Auth | Registration (student/mentor) | ✅ Implemented | ✅ Implemented | ❌ n/a | Implemented |
| Auth | Login / session | ✅ Implemented | ✅ Implemented | ✅ Implemented | Implemented |
| Auth | Logout / password reset | ✅ Implemented | ✅ Implemented | ✅ Implemented | Implemented |
| Auth | Role enforcement | ✅ Implemented | ✅ Implemented | ✅ Implemented | Implemented |
| Mentor Discovery | Browse mentors | ✅ Implemented | ✅ Implemented | ✅ Implemented | Implemented |
| Mentor Discovery | AI Mentor Finder (chat + search) | ✅ Implemented (fallback) | ❌ | ✅ Implemented | Partially implemented |
| Mentor Discovery | Manual filters (field/industry/role/mode) | ✅ Implemented (UI) | ✅ Implemented (UI) | ✅ Implemented (UI) | Implemented |
| Mentor Discovery | Mentor profile detail | ✅ Implemented (UI) | ✅ Implemented (UI) | ✅ Implemented (UI) | Implemented |
| Mentor Discovery | Semantic ranking + explanations | ✅ Backend (OpenRouter+cosine) | ✅ Backend | ✅ Backend | Partially implemented |
| Mentorship | Request submission | ✅ Implemented (backend+UI) | ❌ | ❌ | Implemented |
| Mentorship | Accept / decline | ❌ | ✅ Implemented | ❌ | Implemented |
| Mentorship | Capacity / availability checks | ✅ Backend | ✅ Backend | ✅ Backend | Implemented |
| Mentorship | Meeting scheduling | ✅ UI only | ✅ UI only | ❌ | UI only |
| Mentorship | Meeting notes / transcripts / outcomes | ❌ | ❌ | ❌ | Missing |
| Mentorship | Action items / tasks | ✅ UI only | ✅ UI only | ❌ | UI only |
| Mentorship | End-of-term feedback | ✅ UI only | ✅ UI only | ❌ | UI only |
| Mentorship | Mentorship history / closure | ✅ UI (partial) | ✅ UI (partial) | ❌ | Partially implemented |
| Community | List / create / join / leave | ✅ Implemented | ✅ Implemented | ✅ Implemented | Implemented |
| Community | Group chat | ✅ Implemented | ✅ Implemented | ✅ Implemented | Implemented |
| Community | Reports / moderation | ✅ Implemented (report) | ✅ Implemented (report) | ✅ Admin review flow | Partially implemented |
| Community | Events & webinars | ❌ | ❌ | ❌ | UI only |
| Community | Shared resources | ❌ | ❌ | ❌ | UI only |
| Community | Replies / reactions | ❌ | ❌ | ❌ | Missing |
| Support | Help ticket create / list | ✅ Implemented | ✅ Implemented | ✅ Implemented | Implemented |
| Support | Help ticket reply / resolve | ❌ | ❌ | ✅ Implemented | Implemented |
| Admin | Dashboard | ✅ UI (backend exists) | ❌ | ✅ Implemented | Implemented |
| Admin | Mentor approval | ✅ UI + backend | ✅ Backend | ✅ Implemented | Implemented |
| Admin | Semantic mentor indexing | ✅ Backend | ❌ | ✅ Implemented | Implemented |
| Admin | Account blacklist / activate | ✅ UI (state) | ❌ | ✅ Implemented | Implemented |
| Admin | User status toggle | ✅ Backend | ❌ | ✅ Implemented | Implemented |
| Admin | Statistics / reporting | ✅ UI (CSV) | ❌ | ✅ Implemented | Implemented |
| Admin | Term settings | ✅ UI (state) | ❌ | ✅ Implemented | Implemented |
| Admin | Preference taxonomy management | ❌ | ❌ | ❌ | Missing |
| Admin | Audit logs | ❌ | ❌ | ❌ | Missing |
| Platform | Term deadlines / windows | ✅ Backend + UI | ✅ Backend + UI | ✅ Backend + UI | Implemented |
| Platform | State persistence (JSONB) | ✅ Implemented | ✅ Implemented | ✅ Implemented | Implemented |
| Platform | Storage (mentoring files) | ❌ UI | ❌ UI | ❌ UI | Backend only |

## 2. Per-Feature Detail

### 2.1 Student Features

| Feature | Flow | Status |
|---|---|---|
| Register / login | Supabase Auth + user_profiles | Implemented |
| Student profile | program/goals via state; student_profiles table exists | Partially implemented |
| Career goals | textarea in registration + profile form | Implemented (UI) |
| Browse mentors | /api/state + client filters | Implemented |
| AI search | /api/mentors/search with OpenRouter/cosine + fallback | Partially implemented |
| Manual filters | client-side selects | Implemented |
| Mentor detail + request | modal + create | Implemented |
| My mentorship | accepted request, chat, meetings, tasks, feedback | Partially implemented |
| History | ended relationships | Implemented (partial) |
| Help | tickets | Implemented |
| Communities | join/chat/create/report | Implemented |
| Resources/events | local UI data | UI only |

### 2.2 Mentor Features

| Feature | Flow | Status |
|---|---|---|
| Mentor registration | auto-created pending | Implemented |
| Profile | edit via state | Implemented |
| Approval | admin action | Implemented |
| Requests inbox | accept/decline | Implemented |
| My students | derived | Implemented |
| Tasks/chat | local state | Implemented |
| Meetings/feedback | missing | Missing |
| Community | join/chat | Implemented |

### 2.3 Admin Features

| Feature | Flow | Status |
|---|---|---|
| Dashboard | counts endpoint + UI | Implemented |
| Approvals | approve/deactivate + index | Implemented |
| Blacklist | UI state | Implemented |
| Tickets | reply | Implemented |
| Stats | UI | Implemented |
| Term settings | UI | Implemented |

### 2.4 Cross-Cutting Features

| Feature | Flow | Status |
|---|---|---|
| State persistence | app_state JSONB | Implemented |
| AI matching | OpenRouter embeddings | Partially implemented |
| Security/RBAC | decorators + Supabase JWT | Implemented |

---

## 3. Status Summary

- **Fully implemented end-to-end:** auth, state persistence, mentor listing/filters/AI-search backend,
  mentorship request creation/accept, communities basics, help tickets, admin dashboard/approvals basics.
- **Partially implemented:** AI semantic ranking (backend done, UI fallback, pgvector RPC unused),
  mentorship tracking (UI state vs relational tables), student profile persistence split.
- **UI only:** meetings, feedback, tasks, events, resources, notifications, transcripts.
- **Backend only:** meetings/feedback/actions/transcripts/outcomes, notifications, preference taxonomy,
  audit logs, intervention logs usage.

---

*End of FEATURE_MATRIX.md*
