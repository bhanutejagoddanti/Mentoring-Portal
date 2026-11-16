-- =============================================================================
-- IITM BS Mentoring Portal - SAFE APPLICATION DATABASE RESET
-- =============================================================================
-- PURPOSE
--   Remove ONLY the application's known public-schema tables and their
--   dependent objects so master_setup.sql can rebuild the database from zero.
--
-- BEFORE RUNNING
--   1. Export/backup your database first.
--   2. Confirm you are connected to the intended Supabase project.
--   3. This permanently deletes application data in the listed tables.
--
-- PRESERVED
--   - auth schema and auth.users (user login accounts are NOT deleted)
--   - storage schema, storage buckets, and uploaded storage.objects/files
--   - Supabase-managed schemas, extensions, and unrelated public tables
--   - Any public table not explicitly listed below
--
-- NOTE
--   DROP TABLE ... CASCADE removes dependent foreign keys, triggers, indexes,
--   and RLS policies attached to those tables. The app-owned functions below
--   are dropped separately because they may remain after their tables go.
-- =============================================================================

begin;

-- Remove the app's Storage policy only. Keep the bucket and uploaded files.
drop policy if exists "Authenticated users can access mentoring files"
  on storage.objects;

-- Drop only known IITM BS Mentoring Portal tables.
-- CASCADE handles their foreign-key dependencies regardless of drop order.
drop table if exists
  public.message_reads,
  public.direct_messages,
  public.conversation_participants,
  public.conversations,
  public.community_request_reviews,
  public.community_requests,
  public.help_request_attachments,
  public.help_request_messages,
  public.intervention_logs,
  public.mentor_search_logs,
  public.mentor_vectors,
  public.mentor_credentials,
  public.mentor_availability,
  public.mentor_expertise,
  public.mentor_profiles,
  public.student_profiles,
  public.admin_profiles,
  public.mentorship_outcomes,
  public.action_items,
  public.meeting_transcripts,
  public.meeting_feedback,
  public.meetings,
  public.meeting_proposals,
  public.mentorships,
  public.mentorship_preferences,
  public.mentorship_requests,
  public.career_goals,
  public.preference_options,
  public.academic_terms,
  public.event_registrations,
  public.community_events,
  public.community_resources,
  public.message_reactions,
  public.message_replies,
  public.community_messages,
  public.community_members,
  public.communities,
  public.content_reports,
  public.notifications,
  public.help_requests,
  public.app_state,
  public.user_profiles
cascade;

-- Drop application-owned functions. CASCADE is intentionally not used here;
-- unexpected dependencies should stop the reset rather than remove unrelated objects.
drop function if exists public.match_mentors(vector(1536), integer);
drop function if exists public.match_mentors(vector(1536), double precision, integer);
drop function if exists public.is_active_conversation_participant(uuid);
drop function if exists public.is_conversation_participant_admin(uuid, uuid);
drop function if exists public.is_admin(uuid);
drop function if exists public.set_updated_at();

commit;

-- Post-reset status: these queries should return zero for the listed app tables.
select count(*) as remaining_application_tables
from information_schema.tables
where table_schema = 'public'
  and table_type = 'BASE TABLE'
  and table_name in (
    'user_profiles','student_profiles','mentor_profiles','mentor_credentials',
    'admin_profiles','academic_terms','preference_options','mentorship_requests',
    'mentorship_preferences','mentorships','mentor_expertise','career_goals',
    'mentor_vectors','mentor_search_logs','mentor_availability','meeting_proposals',
    'meetings','meeting_feedback','meeting_transcripts','action_items',
    'mentorship_outcomes','help_requests','intervention_logs','notifications',
    'communities','community_members','community_messages','message_reactions',
    'message_replies','community_events','event_registrations','community_resources',
    'content_reports','app_state','help_request_messages','help_request_attachments',
    'community_requests','community_request_reviews','conversations',
    'conversation_participants','direct_messages','message_reads'
  );

-- Expected result: remaining_application_tables = 0.
