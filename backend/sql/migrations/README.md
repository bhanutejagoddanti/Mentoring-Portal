# Migrations & Database Initialization

## Execution order (Supabase SQL Editor)

Run in this exact order against the Supabase project (`gbccbqvadlhfgfhzztok.supabase.co`):

1. **`backend/supabase_setup.sql`** — base schema:
   - Extensions: `uuid-ossp`, `pgcrypto`, `vector`
   - Tables: `user_profiles`, `student_profiles`, `mentor_profiles`, `mentor_credentials`, `admin_profiles`, `academic_terms`, `preference_options`, `mentorship_requests`, `mentorship_preferences`, `mentorships`, `mentor_expertise`, `career_goals`, `mentor_vectors`, `mentor_search_logs`, `mentor_availability`, `meeting_proposals`, `meetings`, `meeting_feedback`, `meeting_transcripts`, `action_items`, `mentorship_outcomes`, `help_requests`, `intervention_logs`, `notifications`, `communities`, `community_members`, `community_messages`, `message_reactions`, `message_replies`, `community_events`, `event_registrations`, `community_resources`, `content_reports`, `app_state`
   - Indexes, HNSW vector index, `match_mentors` RPC, RLS policies, storage bucket `mentoring-files`, seed academic term.
2. **`backend/sql/migrations/001_help_community_approval.sql`** — help + community-approval tables, triggers, RLS, `is_admin` helper.
3. **`backend/sql/migrations/002_rag_vector_index.sql`** — mentor RAG vectors + `match_mentors` RPC (canonical backend signature) + search logs.
4. **`backend/sql/migrations/003_communication.sql`** — conversations/DMs/read receipts/notifications deep-link columns + messaging RLS policies.

## Master setup file

- **`backend/sql/master_setup.sql`** — one ordered master file containing the full sequence above (base + migrations 001–003). Use this for initial/full setup.

## Database verification

- **`backend/sql/verify_database.sql`** — run after setup; raises if any required table, key column, RLS flag or function is missing.

## Individual migrations

- Migration 001 adds help + community approval tables and RLS policies.
- Migration 002 adds mentor RAG vector index tables and RPC.
- Migration 003 adds the Communication Platform schema:
  - `conversations`, `conversation_participants`, `direct_messages`, `message_reads`
  - `notifications.link` / `notifications.payload` columns
  - RLS enablement + participant-scoped policies for messaging tables.

## Notes

- The Flask API also enforces role checks; RLS is defense-in-depth.
- All tables/policies/migrations are idempotent (`IF NOT EXISTS` / `DROP ... IF EXISTS` / `ON CONFLICT`).
- Does not drop existing data.

## Fix log

- 2026-11: Migration 003 fixed (split `DROP POLICY`/`CREATE POLICY`; DM insert policy uses `new.conversation_id`).
- 2026-11: Migration 001 fixed (`help_requests` policy expression was syntactically invalid).
- 2026-11: Migration 002 fixed (`match_mentors` re-declaration conflict resolved with drop+create).
- 2026-11: Migration 001 extended with backward-compatible `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` for `help_requests` and `intervention_logs` columns missing from the base definitions (fixes `ERROR 42703: column "priority" does not exist`).
