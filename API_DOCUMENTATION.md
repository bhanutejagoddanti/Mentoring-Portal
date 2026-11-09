# IITM BS Mentoring Portal – API Documentation

Source of truth: `backend/app.py` (Flask). Base URL: `http://<host>:5001/api` (frontend uses
`VITE_API_BASE_URL`, default `http://localhost:5001/api`).

All endpoints are prefixed with `/api`. Error responses use JSON bodies such as
`{ "error": "..." }` with appropriate HTTP status codes.

---

## 1. Health

### `GET /api/health`

- **Purpose:** Service liveness + Supabase table/storage connectivity probe.
- **Auth:** None.
- **Response:** `200` with service status, storage readiness, present/missing tables, OpenRouter config.
- **DB tables checked:** `user_profiles`, `student_profiles`, `mentor_profiles`, `academic_terms`,
  `mentorship_requests`, `meetings`, `action_items`, `help_requests`, `communities`, `mentor_vectors`,
  `app_state`.

---

## 2. Authentication

### `POST /api/auth/register`

- **Auth:** None.
- **Body:** `{ name, email, password, role, program?, level?, goals?, job?, industry?, field?,
  linkedin?, slots?, background?, mode? }`; `role` must be `student` or `mentor.
- **Behaviour:** Creates Supabase Auth user (admin API, email confirmed), writes `user_profiles`
  (mentor → pending approval; student → approved), writes role-specific profile rows, syncs state.
- **Response:** `201` `{ message, user }`; errors `400`/`409`.

### `POST /api/auth/login`

- **Auth:** None.
- **Body:** `{ email, password }`.
- **Response:** `200` `{ access_token, refresh_token, user }`; errors `401` (invalid credentials),
  `403` (deactivated / mentor pending approval).

### `GET /api/auth/me`

- **Auth:** Bearer token required (`login_required`).
- **Response:** `200` `{ user: { id, email, name, role, approved, active } }`.

### `POST /api/auth/logout`

- **Auth:** Bearer token (optional usage).
- **Response:** `200 { message }`.

### `POST /api/auth/password-reset`

- **Auth:** None.
- **Body:** `{ email }`.
- **Response:** `200 { message }`.

---

## 3. Mentor Discovery

### `GET /api/mentors`

- **Auth:** Bearer required.
- **Query:** `q`, `field`, `industry`, `mode`.
- **Response:** `200 { items: [...], total }` – approved & active mentors.

### `GET /api/mentors/filter-options`

- **Auth:** Bearer required.
- **Response:** `200 { fields: [], industries: [], modes: [] }`.

### `POST /api/mentors/search`

- **Auth:** Bearer required; **roles:** `student`, `admin`.
- **Body:** `{ query, filters?, limit? }` (`limit` clamped 1–20).
- **Response:** `200 { items: [{ mentor, score, reason }], total, embedding_search, search_method }`.
- **Logic:** capacity filter → optional OpenRouter embedding → cosine similarity → keyword fallback.

---

## 4. Mentor Administration

### `POST /api/admin/mentors/<int:mentor_id>/approve`

- **Auth:** Bearer required; **role:** `admin`.
- **Response:** `200 { message, mentor }`; errors `404`/`409`.

### `POST /api/admin/mentors/<int:mentor_id>/index`

- **Auth:** Bearer required; **role:** `admin`.
- **Response:** `200 { indexed, analysis, has_embedding }`.

---

## 5. Mentorship Requests

### `GET /api/mentorship-requests`

- **Auth:** Bearer required.
- **Response:** `200 { items: [...] }` – scoped by role (student own / mentor assigned / admin all).

### `POST /api/mentorship-requests`

- **Auth:** Bearer required; **role:** `student`.
- **Body:** `{ mentor, goal, message?, term? }`.
- **Validation:** term window open; single request per term; mentor available; capacity; goal required.
- **Response:** `201 { new_req }`; errors `400`/`409`.

### `POST /api/mentorship-requests/<int:req_id>/<decision>`

- **Auth:** Bearer required; **role:** `mentor`.
- **Body:** none (decision in URL).
- **Decision:** `accept` | `decline`; capacity check on accept.
- **Response:** `200 { item }`.

---

## 6. Communities

### `GET /api/communities`

- **Auth:** Bearer required. Returns visible communities with `joined` flags.

### `POST /api/communities`

- **Auth:** Bearer required. Body: `{ name, description?, category?, visibility? }`.

### `POST /api/communities/<int:cid>/join`

- **Auth:** Bearer required.

### `POST /api/communities/<int:cid>/leave`

- **Auth:** Bearer required.

### `GET /api/communities/<int:cid>/messages`

- **Auth:** Bearer required. Returns last 100 messages.

### `POST /api/communities/<int:cid>/messages`

- **Auth:** Bearer required. Body: `{ content }`.

### `POST /api/communities/<int:cid>/report`

- **Auth:** Bearer required. Body: `{ message_id, reason }`.

---

## 7. Help Requests

### `GET /api/help-requests`

- **Auth:** Bearer required. Non-admin sees own tickets.

### `POST /api/help-requests`

- **Auth:** Bearer required. Body: `{ type, description }`.

### `POST /api/help-requests/<int:ticket_id>/reply`

- **Auth:** Bearer required; **role:** `admin`. Body: `{ reply }`.

---

## 8. Admin

### `GET /api/admin/dashboard`

- **Auth:** Bearer required; **role:** `admin`.
- **Response:** `{ students, mentors, pending_approvals, active_mentorships, unmatched_students, open_tickets }`.

### `POST /api/admin/users/<int_or_email>/status`

- **Auth:** Bearer required; **role:** `admin`.
- **Body:** `{ active }`.

---

## 9. Terms & State

### `GET /api/terms/current`

- **Auth:** Bearer required.
- **Response:** current term `{ start, close, end, minMeetings }`.

### `GET /api/state`

- **Auth:** Bearer required. Returns whole app state.

### `PUT /api/state`

- **Auth:** Bearer required. Body: JSON object. Admin allowed unrestricted writes; state persisted via upsert.

---

## 10. Summary of Implemented vs Missing Endpoints

### Implemented (Flask routes present)

Auth (5), Health (1), Mentors (3), Mentor admin (2), Mentorship (3), Communities (6), Help (3), Admin (2), Terms (1), State (2) = **30 routes**.

### Missing / Not implemented (planned in SQL but no route)

- Meetings lifecycle endpoints (`/api/meetings`, scheduling, feedback, transcripts, action items, outcomes).
- Notifications endpoints.
- Events/registrations/resources dedicated endpoints (communities module only partially covers resources).
- Mentor availability, mentor expertise, career goals, preference taxonomy, intervention logs dedicated endpoints.

---

*End of API_DOCUMENTATION.md*
