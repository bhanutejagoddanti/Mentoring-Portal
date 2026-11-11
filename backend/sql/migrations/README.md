# Migrations
Run in Supabase SQL Editor in order.

- Migration 001 adds help + community approval tables and RLS policies.
- Migration 002 adds mentor RAG vector index tables and RPC.
- Migration 003 adds the Communication Platform schema:
  - `conversations`, `conversation_participants`, `direct_messages`, `message_reads`
  - `notifications.link` / `notifications.payload` columns
  - RLS enablement + participant-scoped policies for messaging tables.

The Flask API also enforces role checks; RLS is defense-in-depth. Tables are
IF NOT EXISTS / IF NOT EXISTS columns so re-running is safe. Does not drop data.
