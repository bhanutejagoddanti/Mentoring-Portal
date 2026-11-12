-- =============================================================================
-- IITM BS Mentoring Portal - Database Verification Script (Supabase)
-- =============================================================================
-- Run AFTER backend/sql/master_setup.sql in the Supabase SQL Editor.
-- Checks that every required table, column, foreign key, index, function,
-- extension, RLS flag and policy exists. Raises an exception listing any
-- missing object. Does NOT hide or skip missing objects.
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
  missing_policies text[] := '{}';
  e text[][];
  expected_policies text[][] := ARRAY[
    ARRAY['conversations', 'conversations_select_participant'],
    ARRAY['conversations', 'conversations_insert_own'],
    ARRAY['conversation_participants', 'conversation_participants_select_own'],
    ARRAY['conversation_participants', 'conversation_participants_insert_own'],
    ARRAY['conversation_participants', 'conversation_participants_update_admin'],
    ARRAY['direct_messages', 'direct_messages_participant_select'],
    ARRAY['direct_messages', 'direct_messages_participant_insert'],
    ARRAY['message_reads', 'message_reads_participant_select'],
    ARRAY['message_reads', 'message_reads_participant_insert'],
    ARRAY['message_reads', 'message_reads_participant_update'],
    ARRAY['notifications', 'notifications_own_select'],
    ARRAY['notifications', 'notifications_own_insert'],
    ARRAY['notifications', 'notifications_own_update']
  ];
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

  -- Migration 001-intended columns on existing (base-created) tables
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'help_requests' and column_name = 'priority'
  ) then raise exception 'Missing column: public.help_requests.priority'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'help_requests' and column_name = 'category'
  ) then raise exception 'Missing column: public.help_requests.category'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'help_requests' and column_name = 'assigned_admin'
  ) then raise exception 'Missing column: public.help_requests.assigned_admin'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'help_requests' and column_name = 'confidential'
  ) then raise exception 'Missing column: public.help_requests.confidential'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'intervention_logs' and column_name = 'performed_by'
  ) then raise exception 'Missing column: public.intervention_logs.performed_by'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'intervention_logs' and column_name = 'help_request_id'
  ) then raise exception 'Missing column: public.intervention_logs.help_request_id'; end if;

  -- Communication platform columns
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'conversation_participants' and column_name = 'unread_count'
  ) then raise exception 'Missing column: public.conversation_participants.unread_count'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'direct_messages' and column_name = 'sender_id'
  ) then raise exception 'Missing column: public.direct_messages.sender_id'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'message_reads' and column_name = 'user_id'
  ) then raise exception 'Missing column: public.message_reads.user_id'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'notifications' and column_name = 'link'
  ) then raise exception 'Missing column: public.notifications.link'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'notifications' and column_name = 'payload'
  ) then raise exception 'Missing column: public.notifications.payload'; end if;

  -- Foreign keys must exist
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.conversations'::regclass and contype = 'f'
      and confrelid = 'public.communities'::regclass
  ) then raise exception 'Missing foreign key: public.conversations.community_id -> public.communities.id'; end if;
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.conversations'::regclass and contype = 'f'
      and confrelid = 'public.user_profiles'::regclass
  ) then raise exception 'Missing foreign key: public.conversations.created_by -> public.user_profiles.id'; end if;
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.direct_messages'::regclass and contype = 'f'
      and confrelid = 'public.conversations'::regclass
  ) then raise exception 'Missing foreign key: public.direct_messages.conversation_id -> public.conversations.id'; end if;

  -- Required indexes must exist
  if not exists (
    select 1 from pg_indexes
    where schemaname = 'public' and tablename = 'conversations' and indexname = 'idx_conversations_type'
  ) then raise exception 'Missing index: public.conversations.idx_conversations_type'; end if;
  if not exists (
    select 1 from pg_indexes
    where schemaname = 'public' and tablename = 'direct_messages' and indexname = 'idx_dm_conversation'
  ) then raise exception 'Missing index: public.direct_messages.idx_dm_conversation'; end if;
  if not exists (
    select 1 from pg_indexes
    where schemaname = 'public' and tablename = 'conversation_participants' and indexname = 'idx_cp_user_unread'
  ) then raise exception 'Missing index: public.conversation_participants.idx_cp_user_unread'; end if;

  -- RLS must be enabled on all communication tables
  if not exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'conversations' and rowsecurity) then
    raise exception 'RLS is not enabled on public.conversations';
  end if;
  if not exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'conversation_participants' and rowsecurity) then
    raise exception 'RLS is not enabled on public.conversation_participants';
  end if;
  if not exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'direct_messages' and rowsecurity) then
    raise exception 'RLS is not enabled on public.direct_messages';
  end if;
  if not exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'message_reads' and rowsecurity) then
    raise exception 'RLS is not enabled on public.message_reads';
  end if;
  if not exists (select 1 from pg_tables where schemaname = 'public' and tablename = 'notifications' and rowsecurity) then
    raise exception 'RLS is not enabled on public.notifications';
  end if;

  -- Required functions
  if to_regprocedure('public.is_admin(uuid)') is null then
    raise exception 'Missing function: public.is_admin(uuid)';
  end if;
  if to_regprocedure('public.is_active_conversation_participant(uuid)') is null then
    raise exception 'Missing function: public.is_active_conversation_participant(uuid)';
  end if;
  if to_regprocedure('public.is_conversation_participant_admin(uuid, uuid)') is null then
    raise exception 'Missing function: public.is_conversation_participant_admin(uuid, uuid)';
  end if;
  if to_regprocedure('public.match_mentors(vector(1536), integer)') is null and to_regprocedure('public.match_mentors(vector(1536), integer, integer)') is null then
    raise exception 'Missing function: public.match_mentors';
  end if;

  -- Required policies must exist
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'conversations'
      and policyname = 'conversations_select_participant'
  ) then raise exception 'Missing policy: public.conversations.conversations_select_participant'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'conversations'
      and policyname = 'conversations_insert_own'
  ) then raise exception 'Missing policy: public.conversations.conversations_insert_own'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'conversation_participants'
      and policyname = 'conversation_participants_select_own'
  ) then raise exception 'Missing policy: public.conversation_participants.conversation_participants_select_own'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'conversation_participants'
      and policyname = 'conversation_participants_insert_own'
  ) then raise exception 'Missing policy: public.conversation_participants.conversation_participants_insert_own'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'conversation_participants'
      and policyname = 'conversation_participants_update_admin'
  ) then raise exception 'Missing policy: public.conversation_participants.conversation_participants_update_admin'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'direct_messages'
      and policyname = 'direct_messages_participant_select'
  ) then raise exception 'Missing policy: public.direct_messages.direct_messages_participant_select'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'direct_messages'
      and policyname = 'direct_messages_participant_insert'
  ) then raise exception 'Missing policy: public.direct_messages.direct_messages_participant_insert'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'message_reads'
      and policyname = 'message_reads_participant_select'
  ) then raise exception 'Missing policy: public.message_reads.message_reads_participant_select'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'message_reads'
      and policyname = 'message_reads_participant_insert'
  ) then raise exception 'Missing policy: public.message_reads.message_reads_participant_insert'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'message_reads'
      and policyname = 'message_reads_participant_update'
  ) then raise exception 'Missing policy: public.message_reads.message_reads_participant_update'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'notifications'
      and policyname = 'notifications_own_select'
  ) then raise exception 'Missing policy: public.notifications.notifications_own_select'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'notifications'
      and policyname = 'notifications_own_insert'
  ) then raise exception 'Missing policy: public.notifications.notifications_own_insert'; end if;
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'notifications'
      and policyname = 'notifications_own_update'
  ) then raise exception 'Missing policy: public.notifications.notifications_own_update'; end if;

  -- No anon access on private messaging tables
  if exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename in ('conversations', 'conversation_participants', 'direct_messages', 'message_reads')
      and 'anon' = any(roles)
  ) then
    raise exception 'Unsafe anon policy found on private messaging tables';
  end if;

  -- Required extensions
  if to_regextension('vector') is null then raise exception 'Missing extension: vector'; end if;
  if to_regextension('pgcrypto') is null then raise exception 'Missing extension: pgcrypto'; end if;
  if to_regextension('uuid-ossp') is null then raise exception 'Missing extension: uuid-ossp'; end if;

  raise notice 'DATABASE VERIFICATION OK: all required tables, columns, FKs, indexes, functions, RLS flags and policies are present.';
end $$;
