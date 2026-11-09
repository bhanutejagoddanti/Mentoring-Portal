# IITM BS Mentoring Portal – Complete Project Documentation

> **Scope:** This document is an analysis and architectural/functional report of the existing
> **IITM BS Mentoring Portal** codebase. It is produced from a live inspection of the repository
> (`backend/`, `frontend/`, SQL, configs) and does **not** modify any application code.
> Status labels used throughout: **Implemented**, **Partially implemented**, **UI only**,
> **Backend only**, **Planned**, **Missing**, **Not verified**.

---

## 1. Executive Summary

The **IITM BS Mentoring Portal** is a mentoring and career-support platform for the BS degree
programme at IIT Madras (IITM BS). The application pairs students with industry mentors for
mentorship during an academic term, and adds community, support and administrative layers managed
by the IIC (Industry Interaction Council).

The delivered system has two deployable parts:

1. **React + Vite + Tailwind frontend** (`frontend/`) – single-page application with role-based
   UI (student / mentor / admin).
2. **Flask backend** (`backend/`) – JSON API backed by **Supabase** (Postgres, Auth, Storage, pgvector).

### 1.1 Problem Statement

Mentorship programs in academic settings suffer from fragmented communication: requests,
availability, meetings, progress tracking and support all live in scattered tools or spreadsheets,
and mentor quality/adjustment is hard to manage at programme scale.

### 1.2 Project Objectives

- Enable students to discover suitable industry mentors.
- Enable mentors to receive, evaluate and conduct mentorship requests.
- Track meetings, action items, tasks and end-of-term feedback.
- Provide community discussion spaces, events and shared resources.
- Provide IIC admin oversight: approvals, monitoring, help tickets and reporting.

### 1.3 Expected Outcomes

- A single portal for the full mentorship lifecycle plus community/support functions.

### 1.4 User Interaction Model

- **Student:** browses mentors → gets AI/keyword recommendations → sends request → meets mentor →
  tracks meetings/tasks → gives feedback → joins communities.
- **Mentor:** reviews incoming requests → accepts/declines → manages students → conducts sessions →
  closes mentorship.
- **IIC Admin:** approves mentors, manages accounts/blacklists, monitors stats, handles help tickets,
  configures terms.

---

## 2. Project Overview (Functional Narrative)

The platform is a single-semester mentoring program ("Sep–Dec 2026" term in the current seed data).

- **Term window:** requests are accepted between `term.start` and `term.close` (dates stored as ISO
  strings, e.g. `2026-09-01` / `2026-11-30`).
- **Mentor discovery:** students see approved, active mentors with remaining capacity
  (`slots` minus accepted assignments).
- **AI mentor finder:** a chat-style "Mentor Finder" sends a natural-language query to
  `POST /api/mentors/search`; the backend optionally uses OpenRouter embeddings + cosine similarity,
  falling back to keyword overlap.
- **Mentorship state:** prototype implementation persists a single JSONB `app_state` document that
  holds mentors, requests, students, tasks, meetings, messages, tickets, term and communities.

---

## 3. User Roles and Permissions

### 3.1 Student

Capabilities actually present in the implementation:

| Capability | Implementation |
|---|---|
| Registration | `POST /api/auth/register` with `role=student` (auto-approved) |
| Login | `POST /api/auth/login` (Supabase password sign-in, validated via Bearer token) |
| Profile management | `GET/PUT /api/state` + student profile form (program, goals) |
| Mentor discovery | Reads `/api/state` mentors, client-side filters |
| AI mentor search | `POST /api/mentors/search` (student/admin allowed) with local fallback |
| Mentor request | `POST /api/mentorship-requests` (student only) with term/capacity validation |
| My mentorship | Accepted/ended request, meetings, chat, tasks, feedback |
| History | Past ended mentorships |
| Help | Submit tickets (`POST /api/help-requests`) |
| Communities | List/join/create/chat/report |

### 3.2 Mentor

| Capability | Implementation |
|---|---|
| Login | Supabase sign-in; must be approved (`role=mentor`, `approved=true`) |
| Requests inbox | `GET /api/mentorship-requests` filtered by mentor name |
| Accept/decline | `POST /api/mentorship-requests/<id>/<decision>` (mentor only) |
| My students | Derived from accepted/ended requests |
| Profile | Edit via `/api/state` mentors collection |
| Communities | Join/chat/report |
| History | Past ended relationships |

### 3.3 IIC Administrator

| Capability | Implementation |
|---|---|
| Auth | Supabase account with `role=admin` |
| Approvals | Backend `POST /api/admin/mentors/<id>/approve` + frontend Approvals UI (local state → `/api/state`) |
| Semantic indexing | `POST /api/admin/mentors/<id>/index` (admin) |
| Account status | `POST /api/admin/users/<id>/status` |
| Dashboard | `GET /api/admin/dashboard` |
| Help tickets | Reply via frontend (local state) / backend reply endpoint exists |
| Reports/stats | Frontend statistics + CSV export |
| Term settings | Frontend term editor → `/api/state` |

---

## 4. Feature Modules

### 4.1 Mentor Discovery and AI Matching

**Implemented:**
- Mentor profile fields: name, title, field, industry, role, mode, slots, bio, background, LinkedIn, approved, active.
- OpenRouter LLM call (`openrouter_chat`) for taxonomy extraction (skills, industries, roles, topics, career paths, summary).
- OpenRouter embedding (`text-embedding-3-small`) + cosine similarity (`cosine_similarity`).
- Keyword fallback (`tokenize` + overlap).
- Storage: `mentor_vectors` (pgvector `vector(1536)`, HNSW index, `extracted_metadata`).
- Admin endpoint to index an approved mentor; `POST /api/mentors/search` for students.

**Not implemented / partial:** the pgvector RPC `match_mentors` exists in SQL but the backend currently
computes cosine similarity in Python; the vector lookup previously used the wrong id key (fixed during
this session's analysis).

### 4.2 Mentorship Lifecycle

Implemented stages visible in code: registration → profile → discovery → request → accept/decline →
meetings/tasks/chat → feedback → history/closure.

### 4.3 Community Module

Implemented: community list/create/join/leave/chat/report + local events/resources.

### 4.4 Help / Support

Implemented (prototype): ticket create/list/reply via state + backend endpoints.

### 4.5 Admin / Reporting

Implemented (prototype): dashboard counts, approvals, blacklist, stats, term settings, CSV export.

---

## 5. Dashboard-by-Dashboard Explanation

### 5.1 Student Dashboard – "Browse mentors" (`StudentHome`)

- Widgets: available mentors count, my requests count, current term.
- AI Mentor Finder panel (chat) with prompt shortcuts and backend search results.
- Left column: field filter list. Right column: industry/role/mode filters + mentor cards grid.
- Actions: view mentor → modal with goal/message → send request.

### 5.2 Mentor Dashboard – Requests / My Students

- **Requests:** list incoming (by mentor name), accept/decline pending.
- **My Students:** accepted/ended students, task assignment, chat, end mentorship.

### 5.3 Admin Dashboard

- Cards: students, mentors, open tickets.
- Latest help tickets list.

### 5.4 Admin: Approvals / Students / Mentors / Help Tickets / Statistics / Term Settings

- Tables via reusable `DataTable`; actions via blacklist/activate, approve/deactivate, reply, download report, edit term.

### 5.5 Community Page

- Browse groups, create group, join/leave, chat, events, resources, report modal.

---

## 6. Mentor Discovery and AI Matching – Detailed Flow

1. Mentor registers (`mentor_profiles` upsert, approved=false initially).
2. Admin approves → mentor activated.
3. On approval/state write, backend analyzes profile via OpenRouter and stores `ai_profile` +
   embedding in `mentor_vectors`.
4. Student asks `POST /api/mentors/search {query}` → backend embeds query → cosine similarity against
   mentor vectors → keyword fallback → top-N with reasons.
5. Capacity filter: exclude mentors whose accepted assignments ≥ slots, or `available=false`.

**Real example:** student asks *"I want to work in machine learning"* → embedding-based ranking
returns closest mentors (e.g., ML research mentor) with a human-readable reason.

---

## 7. Mentorship Lifecycle

1. Student registers (approved automatically).
2. Student browses mentors.
3. Student sends request (`goal`, optional `message`, term).
4. Mentor accepts/declines (capacity check).
5. Meetings/tasks/chat tracked via state.
6. End-of-term feedback.
7. History & closure.

---

## 8. Community Module

Public/private communities, join/leave, group chat, reports; events/resources are UI-local.

---

## 9. Database Architecture

See **[DATABASE_DOCUMENTATION.md](./DATABASE_DOCUMENTATION.md)** for the full table-by-table breakdown
and ER diagram.

---

## 10. Backend Architecture

See **[SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)** for backend structure; see
**[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** for endpoints.

---

## 11. Frontend Architecture

React SPA (no router library – page switching via state). See
**[SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)**.

---

## 12. Technology Stack

| Layer | Technology | Implementation Status |
|---|---|---|
| UI framework | React 19.3.1, react-dom | Implemented |
| Build tool | Vite 8.3.5, @vitejs/plugin-react | Implemented |
| Styling | Tailwind CSS 4.3.4 (@tailwindcss/vite) | Implemented |
| Backend | Flask 3 (Flask>=3.0,<4) | Implemented |
| CORS | flask-cors | Implemented |
| Auth/DB client | Supabase Python SDK 2.34.0 | Implemented |
| LLM | OpenRouter (chat + embeddings) | Implemented (optional key) |
| DB | Supabase Postgres + pgvector | Implemented |
| Storage | Supabase Storage (`mentoring-files`) | Provisioned |
| Realtime | Not implemented | Planned |
| Tests | None | Missing |

---

## 13. Security and Privacy

- Supabase Auth (JWT) + Bearer validation server-side.
- Role decorator (`roles(*allowed)`) for admin/mentor routes.
- Service-role key only on server; never in frontend env.
- CORS restricted to configured frontend origin.
- RLS enabled in SQL for key tables (policies included).
- Private storage bucket for mentoring files.

Known gaps: prototype JSONB state endpoint is broadly writable by authenticated users; RLS policies
are defined in SQL but not exercised by the current service-role-backed API design.

---

## 14. Feature Implementation Matrix

See **[FEATURE_MATRIX.md](./FEATURE_MATRIX.md)**.

---

## 15. Testing and Quality

- Frontend: `vite build` executed successfully during this session (24 modules transformed, build OK).
- Backend: smoke-tested over HTTP (health, auth, state, mentors, search, communities, help, mentorship).
- No automated test suite, CI, or database migration tests exist.

---

## 16. Final Deliverables

- This document: `PROJECT_DOCUMENTATION.md`
- System architecture: `SYSTEM_ARCHITECTURE.md`
- API docs: `API_DOCUMENTATION.md`
- Database docs: `DATABASE_DOCUMENTATION.md`
- Feature matrix: `FEATURE_MATRIX.md`

---

## 17. Project Limitations and Future Enhancements

- Single JSONB state document (prototype; normalized tables recommended).
- Meetings/action items/transcripts/feedback persistence via dedicated tables not wired to UI.
- No realtime chat.
- Mentor vector search could use the pgvector RPC.
- No automated tests.

---

## 18. Conclusion

The IITM BS Mentoring Portal currently ships a working end-to-end prototype: React UI ↔ Flask API ↔
Supabase (Auth/Postgres/Storage/pgvector) ↔ OpenRouter AI, with JSONB-backed state for prototype
workflow data and a set of planned-but-not-implemented modules (meetings, transcripts, actions,
realtime, notifications, audit).

---

## 19. Appendix – Key File Reference

```
backend/
  app.py                  # All Flask routes + logic (~1150 lines)
  supabase_setup.sql      # Full Supabase schema
  requirements.txt        # Flask, flask-cors, dotenv, supabase, requests
frontend/
  src/main.jsx             # Entry
  src/App.jsx             # Auth + shell + routing
  src/api.js              # API client
  src/data.js             # Local fallback data/state
  src/ui.jsx              # Reusable UI components
  src/pages/*.jsx         # Feature pages
  src/index.css           # Tailwind + base styles
```

---

*End of PROJECT_DOCUMENTATION.md*
