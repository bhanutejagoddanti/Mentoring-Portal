-- =============================================================================
-- IITM BS Mentoring Portal - Complete Supabase Setup SQL
-- Safe to execute on a fresh or existing Supabase project in the SQL Editor.
-- =============================================================================

-- 1. Enable required extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";
create extension if not exists vector;

-- =============================================================================
-- 2. Authentication & Profiles
-- =============================================================================

create table if not exists public.user_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text unique not null,
  name text not null,
  role text not null check (role in ('student', 'mentor', 'admin')),
  approved boolean not null default false,
  active boolean not null default true,
  avatar_url text,
  phone text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.student_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.user_profiles(id) on delete cascade,
  program text default 'BS Data Science',
  level text default 'Level 1',
  goals text,
  interests text[] default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.mentor_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.user_profiles(id) on delete cascade,
  title text,
  role text,
  field text,
  industry text,
  bio text,
  background text,
  linkedin text,
  mode text default 'Online',
  slots integer not null default 2,
  hours text default '3-5 hours',
  available boolean not null default true,
  ai_profile jsonb not null default '{}'::jsonb,
  profile_indexed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.mentor_credentials (
  id uuid primary key default gen_random_uuid(),
  mentor_id uuid not null references public.mentor_profiles(id) on delete cascade,
  credential_type text default 'degree',
  title text not null,
  issuer text,
  year text,
  document_url text,
  verified boolean not null default false,
  verified_by uuid references public.user_profiles(id),
  created_at timestamptz not null default now()
);

create table if not exists public.admin_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.user_profiles(id) on delete cascade,
  department text default 'IIC',
  permissions text[] default array['all'],
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- =============================================================================
-- 3. Mentorship & Terms
-- =============================================================================

create table if not exists public.academic_terms (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  start_date date not null,
  close_date date not null,
  end_date date not null,
  min_meetings integer not null default 3,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.preference_options (
  id uuid primary key default gen_random_uuid(),
  category text not null,
  label text not null,
  value text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.mentorship_requests (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references public.user_profiles(id) on delete cascade,
  mentor_id uuid references public.user_profiles(id) on delete set null,
  student_name text,
  student_email text,
  mentor_name text,
  term_id uuid references public.academic_terms(id) on delete set null,
  term_name text not null,
  goal text not null,
  message text,
  preferences jsonb not null default '[]'::jsonb,
  status text not null default 'Pending' check (status in ('Pending', 'Accepted', 'Declined', 'Ended', 'Cancelled')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.mentorship_preferences (
  id uuid primary key default gen_random_uuid(),
  request_id uuid not null references public.mentorship_requests(id) on delete cascade,
  preference_key text not null,
  preference_value text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.mentorships (
  id uuid primary key default gen_random_uuid(),
  request_id uuid references public.mentorship_requests(id) on delete cascade,
  student_id uuid not null references public.user_profiles(id) on delete cascade,
  mentor_id uuid not null references public.user_profiles(id) on delete cascade,
  term_id uuid references public.academic_terms(id) on delete set null,
  status text not null default 'Active' check (status in ('Active', 'Completed', 'Terminated')),
  start_date timestamptz not null default now(),
  end_date timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.mentor_expertise (
  id uuid primary key default gen_random_uuid(),
  mentor_id uuid not null references public.mentor_profiles(id) on delete cascade,
  skill text not null,
  level text,
  years integer,
  created_at timestamptz not null default now()
);

create table if not exists public.career_goals (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.student_profiles(id) on delete cascade,
  goal_title text not null,
  target_timeline text,
  status text not null default 'In Progress',
  created_at timestamptz not null default now()
);

-- =============================================================================
-- 4. Mentor Semantic Search & Vector Embeddings
-- =============================================================================

create table if not exists public.mentor_vectors (
  id uuid primary key default gen_random_uuid(),
  mentor_id uuid not null unique references public.mentor_profiles(id) on delete cascade,
  embedding vector(1536),
  extracted_metadata jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.mentor_search_logs (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references public.user_profiles(id) on delete set null,
  query text not null,
  filters jsonb not null default '{}'::jsonb,
  result_count integer not null default 0,
  created_at timestamptz not null default now()
);

-- =============================================================================
-- 5. Meetings, Action Items & Progress
-- =============================================================================

create table if not exists public.mentor_availability (
  id uuid primary key default gen_random_uuid(),
  mentor_id uuid not null references public.mentor_profiles(id) on delete cascade,
  day_of_week text not null,
  start_time text not null,
  end_time text not null,
  timezone text not null default 'Asia/Kolkata',
  created_at timestamptz not null default now()
);

create table if not exists public.meeting_proposals (
  id uuid primary key default gen_random_uuid(),
  mentorship_id uuid references public.mentorships(id) on delete cascade,
  proposed_by uuid not null references public.user_profiles(id) on delete cascade,
  proposed_time timestamptz not null,
  status text not null default 'Proposed' check (status in ('Proposed', 'Accepted', 'Rejected', 'Cancelled')),
  created_at timestamptz not null default now()
);

create table if not exists public.meetings (
  id uuid primary key default gen_random_uuid(),
  mentorship_id uuid references public.mentorships(id) on delete cascade,
  student_name text,
  mentor_name text,
  scheduled_at timestamptz not null,
  status text not null default 'Scheduled' check (status in ('Scheduled', 'Completed', 'Cancelled', 'NoShow')),
  meeting_link text,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.meeting_feedback (
  id uuid primary key default gen_random_uuid(),
  meeting_id uuid not null references public.meetings(id) on delete cascade,
  submitted_by uuid not null references public.user_profiles(id) on delete cascade,
  rating integer not null check (rating >= 1 and rating <= 5),
  comments text,
  created_at timestamptz not null default now()
);

create table if not exists public.meeting_transcripts (
  id uuid primary key default gen_random_uuid(),
  meeting_id uuid not null references public.meetings(id) on delete cascade,
  storage_path text not null,
  summary text,
  created_at timestamptz not null default now()
);

create table if not exists public.action_items (
  id uuid primary key default gen_random_uuid(),
  mentorship_id uuid references public.mentorships(id) on delete cascade,
  student_name text not null,
  title text not null,
  due_date date,
  done boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.mentorship_outcomes (
  id uuid primary key default gen_random_uuid(),
  mentorship_id uuid not null references public.mentorships(id) on delete cascade,
  rating integer check (rating >= 1 and rating <= 5),
  feedback text,
  student_summary text,
  mentor_summary text,
  created_at timestamptz not null default now()
);

-- =============================================================================
-- 6. Support & Help System
-- =============================================================================

create table if not exists public.help_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.user_profiles(id) on delete cascade,
  user_name text not null,
  user_email text,
  role text not null check (role in ('student', 'mentor', 'admin')),
  ticket_type text not null,
  description text not null,
  status text not null default 'Open' check (status in ('Open', 'In Progress', 'Resolved', 'Closed')),
  reply text not null default '',
  resolved_by uuid references public.user_profiles(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.intervention_logs (
  id uuid primary key default gen_random_uuid(),
  ticket_id uuid not null references public.help_requests(id) on delete cascade,
  admin_id uuid not null references public.user_profiles(id),
  action_taken text not null,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.user_profiles(id) on delete cascade,
  title text not null,
  message text not null,
  read boolean not null default false,
  type text not null default 'info',
  created_at timestamptz not null default now()
);

-- =============================================================================
-- 7. Communities & Events
-- =============================================================================

create table if not exists public.communities (
  id uuid primary key default gen_random_uuid(),
  name text unique not null,
  description text,
  category text not null default 'General',
  visibility text not null default 'public' check (visibility in ('public', 'private')),
  creator_id uuid references public.user_profiles(id) on delete set null,
  avatar_url text,
  is_archived boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.community_members (
  id uuid primary key default gen_random_uuid(),
  community_id uuid not null references public.communities(id) on delete cascade,
  user_id uuid not null references public.user_profiles(id) on delete cascade,
  role text not null default 'member' check (role in ('owner', 'admin', 'moderator', 'member')),
  status text not null default 'active' check (status in ('active', 'pending', 'banned')),
  joined_at timestamptz not null default now(),
  unique(community_id, user_id)
);

create table if not exists public.community_messages (
  id uuid primary key default gen_random_uuid(),
  community_id uuid not null references public.communities(id) on delete cascade,
  sender_id uuid references public.user_profiles(id) on delete set null,
  sender_name text not null,
  content text not null,
  is_pinned boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.message_reactions (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references public.community_messages(id) on delete cascade,
  user_id uuid not null references public.user_profiles(id) on delete cascade,
  reaction text not null,
  created_at timestamptz not null default now(),
  unique(message_id, user_id, reaction)
);

create table if not exists public.message_replies (
  id uuid primary key default gen_random_uuid(),
  parent_message_id uuid not null references public.community_messages(id) on delete cascade,
  sender_id uuid references public.user_profiles(id) on delete set null,
  sender_name text not null,
  content text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.community_events (
  id uuid primary key default gen_random_uuid(),
  community_id uuid not null references public.communities(id) on delete cascade,
  title text not null,
  description text,
  event_date timestamptz not null,
  location text,
  meeting_link text,
  host_id uuid references public.user_profiles(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.event_registrations (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.community_events(id) on delete cascade,
  user_id uuid not null references public.user_profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  unique(event_id, user_id)
);

create table if not exists public.community_resources (
  id uuid primary key default gen_random_uuid(),
  community_id uuid not null references public.communities(id) on delete cascade,
  title text not null,
  resource_type text not null default 'link',
  url text not null,
  description text,
  uploaded_by uuid references public.user_profiles(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.content_reports (
  id uuid primary key default gen_random_uuid(),
  reported_by uuid not null references public.user_profiles(id) on delete cascade,
  community_id uuid references public.communities(id) on delete cascade,
  message_id uuid references public.community_messages(id) on delete cascade,
  reason text not null,
  status text not null default 'Pending' check (status in ('Pending', 'Reviewed', 'Dismissed', 'Actioned')),
  created_at timestamptz not null default now()
);

-- Backward compatibility state store for state snapshots
create table if not exists public.app_state (
  id integer primary key check (id = 1),
  payload jsonb not null,
  updated_at timestamptz not null default now()
);

-- =============================================================================
-- 8. Indexes for High Performance
-- =============================================================================

create index if not exists idx_user_profiles_role on public.user_profiles(role);
create index if not exists idx_user_profiles_email on public.user_profiles(email);
create index if not exists idx_mentor_profiles_field on public.mentor_profiles(field);
create index if not exists idx_mentor_profiles_industry on public.mentor_profiles(industry);
create index if not exists idx_mentor_profiles_available on public.mentor_profiles(available);
create index if not exists idx_mentorship_requests_student on public.mentorship_requests(student_id);
create index if not exists idx_mentorship_requests_mentor on public.mentorship_requests(mentor_id);
create index if not exists idx_mentorship_requests_status on public.mentorship_requests(status);
create index if not exists idx_mentorship_requests_term on public.mentorship_requests(term_name);
create index if not exists idx_meetings_mentorship on public.meetings(mentorship_id);
create index if not exists idx_action_items_mentorship on public.action_items(mentorship_id);
create index if not exists idx_action_items_student on public.action_items(student_name);
create index if not exists idx_community_messages_community on public.community_messages(community_id);
create index if not exists idx_community_members_user on public.community_members(user_id);
create index if not exists idx_help_requests_user on public.help_requests(user_id);
create index if not exists idx_help_requests_status on public.help_requests(status);

-- Vector Cosine Distance Index (HNSW for fast approximate nearest neighbor search)
create index if not exists idx_mentor_vectors_hnsw on public.mentor_vectors
  using hnsw (embedding vector_cosine_ops);

-- =============================================================================
-- 9. Semantic Mentor Search RPC Function (pgvector)
-- =============================================================================

create or replace function public.match_mentors (
  query_embedding vector(1536),
  match_threshold float default 0.2,
  match_count int default 5
)
returns table (
  mentor_id uuid,
  user_id uuid,
  name text,
  title text,
  field text,
  industry text,
  similarity float
)
language plpgsql
security definer
as $$
begin
  return query
  select
    mp.id as mentor_id,
    up.id as user_id,
    up.name,
    mp.title,
    mp.field,
    mp.industry,
    1 - (mv.embedding <=> query_embedding) as similarity
  from public.mentor_vectors mv
  join public.mentor_profiles mp on mp.id = mv.mentor_id
  join public.user_profiles up on up.id = mp.user_id
  where up.approved = true
    and up.active = true
    and mp.available = true
    and (1 - (mv.embedding <=> query_embedding)) >= match_threshold
  order by mv.embedding <=> query_embedding asc
  limit match_count;
end;
$$;

-- =============================================================================
-- 10. Row Level Security (RLS) Configuration
-- =============================================================================

alter table public.user_profiles enable row level security;
alter table public.student_profiles enable row level security;
alter table public.mentor_profiles enable row level security;
alter table public.mentor_credentials enable row level security;
alter table public.admin_profiles enable row level security;
alter table public.academic_terms enable row level security;
alter table public.preference_options enable row level security;
alter table public.mentorship_requests enable row level security;
alter table public.mentorship_preferences enable row level security;
alter table public.mentorships enable row level security;
alter table public.mentor_expertise enable row level security;
alter table public.career_goals enable row level security;
alter table public.mentor_vectors enable row level security;
alter table public.mentor_search_logs enable row level security;
alter table public.mentor_availability enable row level security;
alter table public.meeting_proposals enable row level security;
alter table public.meetings enable row level security;
alter table public.meeting_feedback enable row level security;
alter table public.meeting_transcripts enable row level security;
alter table public.action_items enable row level security;
alter table public.mentorship_outcomes enable row level security;
alter table public.help_requests enable row level security;
alter table public.intervention_logs enable row level security;
alter table public.notifications enable row level security;
alter table public.communities enable row level security;
alter table public.community_members enable row level security;
alter table public.community_messages enable row level security;
alter table public.message_reactions enable row level security;
alter table public.message_replies enable row level security;
alter table public.community_events enable row level security;
alter table public.event_registrations enable row level security;
alter table public.community_resources enable row level security;
alter table public.content_reports enable row level security;
alter table public.app_state enable row level security;

-- Drop existing policies if they exist before recreating to ensure idempotency
drop policy if exists "Public can view approved active mentors" on public.mentor_profiles;
drop policy if exists "Users can view own profile" on public.user_profiles;
drop policy if exists "Users can update own profile" on public.user_profiles;
drop policy if exists "Community read access" on public.communities;
drop policy if exists "Community messages read access" on public.community_messages;
drop policy if exists "Community messages insert access" on public.community_messages;
drop policy if exists "Students view own requests" on public.mentorship_requests;
drop policy if exists "Students insert own requests" on public.mentorship_requests;
drop policy if exists "Terms viewable by authenticated users" on public.academic_terms;

-- 1. Profiles
create policy "Public can view approved active mentors"
  on public.mentor_profiles for select
  using (exists (
    select 1 from public.user_profiles up
    where up.id = mentor_profiles.user_id and up.approved = true and up.active = true
  ));

create policy "Users can view own profile"
  on public.user_profiles for select
  using (auth.uid() = id);

create policy "Users can update own profile"
  on public.user_profiles for update
  using (auth.uid() = id);

-- 2. Communities: visible if public or member or admin
create policy "Community read access"
  on public.communities for select
  using (
    visibility = 'public'
    or exists (
      select 1 from public.community_members cm
      where cm.community_id = communities.id and cm.user_id = auth.uid() and cm.status = 'active'
    )
    or exists (
      select 1 from public.user_profiles up
      where up.id = auth.uid() and up.role = 'admin'
    )
  );

create policy "Community messages read access"
  on public.community_messages for select
  using (
    exists (
      select 1 from public.communities c
      where c.id = community_messages.community_id and (
        c.visibility = 'public'
        or exists (
          select 1 from public.community_members cm
          where cm.community_id = c.id and cm.user_id = auth.uid() and cm.status = 'active'
        )
      )
    )
    or exists (
      select 1 from public.user_profiles up
      where up.id = auth.uid() and up.role = 'admin'
    )
  );

create policy "Community messages insert access"
  on public.community_messages for insert
  with check (
    auth.uid() = sender_id
    and exists (
      select 1 from public.community_members cm
      where cm.community_id = community_messages.community_id and cm.user_id = auth.uid() and cm.status = 'active'
    )
  );

-- 3. Mentorship requests
create policy "Students view own requests"
  on public.mentorship_requests for select
  using (
    student_id = auth.uid()
    or mentor_id = auth.uid()
    or exists (select 1 from public.user_profiles where id = auth.uid() and role = 'admin')
  );

create policy "Students insert own requests"
  on public.mentorship_requests for insert
  with check (student_id = auth.uid());

-- 4. Academic terms viewable by all authenticated users
create policy "Terms viewable by authenticated users"
  on public.academic_terms for select
  using (true);

-- =============================================================================
-- 11. Storage Bucket Provisioning
-- =============================================================================

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'mentoring-files',
  'mentoring-files',
  false,
  20971520, -- 20 MB limit
  array['application/pdf', 'image/png', 'image/jpeg', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
)
on conflict (id) do update set
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "Authenticated users can access mentoring files" on storage.objects;
create policy "Authenticated users can access mentoring files"
  on storage.objects for all
  using (bucket_id = 'mentoring-files' and auth.role() = 'authenticated')
  with check (bucket_id = 'mentoring-files' and auth.role() = 'authenticated');

-- =============================================================================
-- 12. Seed Default Academic Term
-- =============================================================================

insert into public.academic_terms (name, start_date, close_date, end_date, min_meetings, is_active)
values ('Sep–Dec 2026', '2026-09-01', '2026-11-30', '2026-12-20', 3, true)
on conflict do nothing;
