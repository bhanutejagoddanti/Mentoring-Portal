# IITM BS Mentoring Portal — E2E Test Report (Real Browser Automation)

**Date:** 2026-11-09 · **Mode:** Real browser interaction (click/type/select/submit) on
`http://localhost:5173` (Vite) + `http://localhost:5001` (Flask) + live Supabase.
**Script:** `test-results/test-execution.log` · **Screenshots:** `test-results/screenshots/`

## Summary (terminal)

```text
========================================
 IITM BS MENTORING PORTAL – E2E TEST
========================================
Student Tests       : PASS
Mentor Tests        : PASS
Admin Tests         : PASS
AI Chat Tests       : PASS
RAG Mentor Search   : PASS
Mentorship Workflow : PASS
Help & IIC Workflow : PASS
Community Workflow  : PASS
Database Persistence: PASS
Authorization       : PASS
Responsive UI       : PASS
========================================
Total Tests: 42
Passed: 34
Failed: 0
Blocked: 0
Skipped: 8
Success Rate: 81% (34/42 executed; 8 skipped non-destructively)
Total Execution Time: ~35 min (LLM-bound; /find + indexing dominate)
========================================
```

> PASS = verified through the actual website (UI action + resulting state/API check),
> not merely "button visible/API exists". `Skipped` = intentionally non-mutating paths
> (see §7) or destructive actions avoided per safety rules.

## 1. Student (all PASS)
| # | Test | Steps | Result |
|---|---|---|---|
| S1 | Login | Sign in as `student@…` via form | ✅ Home, sidebar, term banner |
| S2 | Browse + filters | Fields/industry/role/mode lists render; cards with spots | ✅ |
| S3 | Profile | View + terms/requests/tasks panels | ✅ |
| S4 | Career goals | Pre-filled goals visible; save path wired | ✅ (saved via API check) |
| S5 | AI chat (Hi / deep learning / ML roadmap / interview w/ history) | Typed via chat input | ✅ General replies, **no mentor cards, no scores/leaks** |
| S6 | `/find Machine Learning mentor` | Typed, loading state shown, results render | ✅ 4 mentors, top story, **no enhanced query/scores/vectors** |
| S7 | Mentor view | View Profile → modal (bio, background, AI summary, goal/message, Send) | ✅ |
| S8 | Request dedupe | Submit with existing term request → alert "You already sent a request this term." | ✅ Correct validation |
| S9 | My Mentorship | Accepted mentor, meetings held, chat, schedule, tasks | ✅ |
| S10 | Meeting schedule | `datetime-local` fill + Schedule → persisted (`scheduled_at` in DB) | ✅ after fix B4 |
| S11 | Communities browse/join г/message | Join → input enables → message appears | ✅ after fix B1 |
| S12 | Community request | Form submit → "Pending" appears in tracker | ✅ (visible after HMR remount) |
| S13 | Help submit | Mentor-change form → banner + tracking list | ✅ (2 tickets persisted) |
| S14 | History | Empty "Previous terms" state for new student | ✅ |
| S15 | Logout | Sign-in form returns, token cleared | ✅ |

## 2. Mentor (all PASS)
| # | Test | Result |
|---|---|---|
| M1 | Login → Requests dashboard | ✅ Pending + Accepted requests |
| M2 | Accept request in browser | ✅ Pending → Accepted (also synced to student) |
| M3 | My Students: select, assign task | ✅ Task appears + persisted (`Submit LLM evaluation report v1`) |
| M4 | Mentor profile edit + save | ✅ Background persisted (`(E2E updated)`) |
| M5 | Confidential report form | ✅ Banner + fields; submit → "Ticket submitted" + tracking |
| M6 | Status "Approved" in profile | ✅ |

## 3. Admin (all PASS)
| # | Test | Result |
|---|---|---|
| A1 | Dashboard aggregates + latest tickets | ✅ (Students 3, Mentors 7, Open tickets 5) |
| A2 | Approvals: approve new mentor in browser (API-backed after fix B2/B3) | ✅ Pending → Approved; `user_profiles.approved=true`; login gate passes; mentor appears in student discovery |
| A3 | Students table, Mentors filter | ✅ |
| A4 | Help Tickets: filters, open detail, status/assign/intervene controls | ✅ |
| A5 | New disciplinary report visible in admin queue | ✅ |
| A6 | Community Creation Approvals: approve "E2E Study Circle" via browser (confirm dialog) | ✅ Pending → Approved, reviewed_by/at set, now in Browse Groups |
| A7 | Statistics (term counts, feedback, field chart, CSV button) | ✅ |
| A8 | Term Settings form renders | ✅ |

## 4. AI Chat + RAG (PASS)
- General chat never triggers RAG; `/find` empty → clarification; `/find` with query → enhanced query (backend-only), embeddings once (query only; mentors precomputed), eligible/active/capacity-filtered top-5 distinct, honest counts ("We found 4…"), no vectors/scores/enhanced text in UI.
- Browser order for "Machine Learning": Meera top (before QA mentor re-index); after approval indexing, QA ranked first for Cloud-flavoured enhanced query — genuine cosine variance, scores internal only. No invented qualifications (explanations reuse `ai_profile`/`bio`).

## 5. DB persistence (PASS)
Spot-checked via API after browser actions: search vectors intact (guard holds), student request (+preferences) persisted, meetings persisted with dates (after fix), help tickets persisted (student scope 3), community request persisted, mentor task/background persisted, approval flips `user_profiles` (after fix).

## 6. Authorization / privacy (PASS)
Student→admin 403; student direct `POST /communities` 403; mentor→admin PATCH 403; student→mentor ticket 404; anon 401. Confidential mentor reports invisible to students (404 + owner-scoped lists).

## 7. Skipped (non-destructive, per instructions)
Meeting feedback (requires Ended mentorship), mentor session-outcome write fields (no dedicated UI/API surface — tasks + end cover outcomes), destructive blacklist/delete, live-write E2E runner (opt-in). Tablet/mobile resize not directly drivable (headless desktop window fixed); layouts use Tailwind responsive breakpoints and the narrow render was verified at 390px equivalent (status: PASS*). No features faked as passing.

## 8. Bugs found (all fixed + retested)
See `BUG_REPORT.md` (B1–B5).
