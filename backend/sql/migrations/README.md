# Migrations
Run in Supabase SQL Editor in order. Migration 001 adds help + community
approval tables and RLS policies. The Flask API also enforces role checks;
RLS is defense-in-depth. Tables are IF NOT EXISTS so re-running is safe.
