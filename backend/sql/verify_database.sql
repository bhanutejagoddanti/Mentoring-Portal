-- =============================================================================
-- IITM BS Mentoring Portal - Database Verification Script (Supabase)
-- =============================================================================
-- Run AFTER backend/sql/master_setup.sql in the Supabase SQL Editor.
-- Checks that every required table, key column, RLS flag and function exists.
-- Raises an exception (aborting the script) listing any missing object.
-- =============================================================================

do $$
declare
  required_tables text[] := ARRAY[
    'public.app_state',
    'public.user_profiles',
    'public.student_profiles',
    'public.mentor_profiles',
    'public.mentor_credentials',
    'public.admin_profiles',
    'public.academic_terms',
    'public.preference_options',
    'public.mentorship_requests',
    'public.mentorship_preferences',
    'public.mentorships',
    'public.mentor_expertise',
    'public.career_goals',
    'public.mentor_vectors',
    'public.mentor_search_logs',
    'public.mentor_availability',
    'public.meeting_proposals',
    'public.meetings',
    'public.meeting_feedback',
    'public.meeting_transcripts',
    'public.action_items',
    'public.mentorship_outcomes',
    'public.help_requests',
    'public.intervention_logs',
    'public.notifications',
    'public.communities',
    'public.community_members',
    'public.community_messages',
    'public.message_reactions',
    'public.message_replies',
    'public.community_events',
    'public.event_registrations',
    'public.community_resources',
    'public.content_reports',
    'public.conversations',
    'public.conversation_participants',
    'public.direct_messages',
    'public.message_reads'
  ];
  missing_tables text[] := '{}';
  t text;
begin
  foreach t in array required_tables loop
    if to_regclass(t) is null then
      missing_tables := array_append(missing_tables, t);
    end if;
  end loop;

  if array_length(missing_tables, 1) > 0 then
    raise exception 'Missing required tables: %', array_to_string(missing_tables, ', ');
  end if;

  -- Key column assertions
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'user_profiles' and column_name = 'id'
  ) then raise exception 'Missing column: public.user_profiles.id'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'notifications' and column_name = 'user_id'
  ) then raise exception 'Missing column: public.notifications.user_id'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'conversations' and column_name = 'type'
  ) then raise exception 'Missing column: public.conversations.type'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'direct_messages' and column_name = 'conversation_id'
  ) then raise exception 'Missing column: public.direct_messages.conversation_id'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'message_reads' and column_name = 'conversation_id'
  ) then raise exception 'Missing column: public.message_reads.conversation_id'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'mentor_vectors' and column_name = 'embedding'
  ) then raise exception 'Missing column: public.mentor_vectors.embedding'; end if;

  -- RLS must be enabled on the messaging tables
  if not exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'conversations' and rowsecurity) then
    raise exception 'RLS is not enabled on public.conversations';
  end if;
  if not exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'direct_messages' and rowsecurity) then
    raise exception 'RLS is not enabled on public.direct_messages';
  end if;
  if not exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'notifications' and rowsecurity) then
    raise exception 'RLS is not enabled on public.notifications';
  end if;

  -- Required functions
  if to_regprocedure('public.is_admin(uuid)') is null then
    raise exception 'Missing function: public.is_admin(uuid)';
  end if;
  if to_regprocedure('public.match_mentors(vector(1536), integer)') is null and to_regprocedure('public.match_mentors(vector(1536), integer, integer)') is null then
    raise exception 'Missing function: public.match_mentors';
  end if;

  -- Required extensions
  if to_regextension('vector') is null then raise exception 'Missing extension: vector'; end if;
  if to_regextension('pgcrypto') is null then raise exception 'Missing extension: pgcrypto'; end if;

  raise notice 'DATABASE VERIFICATION OK: all required tables, key columns, RLS flags and functions are present.';
end $$;
