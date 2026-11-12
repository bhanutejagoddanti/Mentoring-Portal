-- =============================================================================
-- IITM BS Mentoring Portal - Migration 003: Communication Platform (Inbox/DM)
-- Adds direct messaging + conversation infrastructure on top of the existing
-- Supabase schema (user_profiles, communities, community_messages,
-- notifications, content_reports, app_state).
--
-- Safe to run repeatedly (IF NOT EXISTS / IF NOT EXISTS columns / DROP POLICY IF EXISTS).
-- Does not drop existing tables or records.
-- =============================================================================

create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- -----------------------------------------------------------------------------
-- Conversations (direct messages + typed community conversations)
-- -----------------------------------------------------------------------------
create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  type text not null default 'direct' check (type in ('direct', 'community')),
  community_id uuid references public.communities(id) on delete set null,
  created_by uuid references public.user_profiles(id) on delete set null,
  status text not null default 'active' check (status in ('active', 'archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  last_message_at timestamptz
);

create index if not exists idx_conversations_type on public.conversations(type);
create index if not exists idx_conversations_created_by on public.conversations(created_by);
create index if not exists idx_conversations_last_message on public.conversations(last_message_at desc);

-- -----------------------------------------------------------------------------
-- Conversation participants
-- -----------------------------------------------------------------------------
create table if not exists public.conversation_participants (
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  user_id uuid not null references public.user_profiles(id) on delete cascade,
  role text not null default 'member' check (role in ('owner', 'admin', 'moderator', 'member')),
  status text not null default 'active' check (status in ('active', 'pending', 'banned')),
  last_read_at timestamptz not null default now(),
  unread_count integer not null default 0,
  joined_at timestamptz not null default now(),
  primary key (conversation_id, user_id)
);

create index if not exists idx_cp_conversation on public.conversation_participants(conversation_id);
create index if not exists idx_cp_user on public.conversation_participants(user_id);
create index if not exists idx_cp_user_unread on public.conversation_participants(user_id, unread_count);

-- -----------------------------------------------------------------------------
-- Direct messages
-- -----------------------------------------------------------------------------
create table if not exists public.direct_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  sender_id uuid references public.user_profiles(id) on delete set null,
  sender_name text not null,
  sender_role text not null default 'student',
  content text not null,
  reply_to_id uuid references public.direct_messages(id) on delete set null,
  attachments jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_dm_conversation on public.direct_messages(conversation_id, created_at desc);
create index if not exists idx_dm_sender on public.direct_messages(sender_id);

-- -----------------------------------------------------------------------------
-- Message reads (read receipts / unread tracking)
-- -----------------------------------------------------------------------------
create table if not exists public.message_reads (
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  user_id uuid not null references public.user_profiles(id) on delete cascade,
  last_read_message_id uuid references public.direct_messages(id) on delete set null,
  last_read_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (conversation_id, user_id)
);

create index if not exists idx_mr_conversation_user on public.message_reads(conversation_id, user_id);
create index if not exists idx_mr_user on public.message_reads(user_id);

-- -----------------------------------------------------------------------------
-- Notifications: add deep-link + payload support for navigation from inbox
-- -----------------------------------------------------------------------------
alter table public.notifications add column if not exists link text not null default '';
alter table public.notifications add column if not exists payload jsonb not null default '{}'::jsonb;

-- -----------------------------------------------------------------------------
-- RLS: enable on all communication tables
-- -----------------------------------------------------------------------------
alter table public.conversations enable row level security;
alter table public.conversation_participants enable row level security;
alter table public.direct_messages enable row level security;
alter table public.message_reads enable row level security;
alter table public.notifications enable row level security;

-- -----------------------------------------------------------------------------
-- Helper: SECURITY DEFINER (fixed search_path, no RLS recursion) to check
-- whether the current authenticated user is an active participant.
-- -----------------------------------------------------------------------------
create or replace function public.is_active_conversation_participant(p_conversation_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select auth.uid() is not null and exists (
    select 1
    from public.conversation_participants cp
    where cp.conversation_id = p_conversation_id
      and cp.user_id = auth.uid()
      and cp.status = 'active'
  );
$$;

create or replace function public.is_conversation_participant_admin(p_conversation_id uuid, p_user_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.conversation_participants cp
    where cp.conversation_id = p_conversation_id
      and cp.user_id = p_user_id
      and cp.status = 'active'
      and cp.role in ('owner', 'admin')
  );
$$;

revoke all on function public.is_active_conversation_participant(uuid) from public;
grant execute on function public.is_active_conversation_participant(uuid) to authenticated, service_role;
revoke all on function public.is_conversation_participant_admin(uuid, uuid) from public;
grant execute on function public.is_conversation_participant_admin(uuid, uuid) to authenticated, service_role;

-- -----------------------------------------------------------------------------
-- RLS policies: conversations (participant-scoped reads, owner self-insert)
-- -----------------------------------------------------------------------------
drop policy if exists "conversations_select_participant" on public.conversations;
create policy "conversations_select_participant" on public.conversations
  for select to authenticated
  using (public.is_active_conversation_participant(id));

drop policy if exists "conversations_insert_own" on public.conversations;
create policy "conversations_insert_own" on public.conversations
  for insert to authenticated
  with check (auth.uid() = created_by);

-- -----------------------------------------------------------------------------
-- RLS policies: conversation participants (self read/insert; admin update)
-- -----------------------------------------------------------------------------
drop policy if exists "conversation_participants_select_own" on public.conversation_participants;
create policy "conversation_participants_select_own" on public.conversation_participants
  for select to authenticated
  using (user_id = auth.uid());

drop policy if exists "conversation_participants_insert_own" on public.conversation_participants;
create policy "conversation_participants_insert_own" on public.conversation_participants
  for insert to authenticated
  with check (user_id = auth.uid());

drop policy if exists "conversation_participants_update_admin" on public.conversation_participants;
create policy "conversation_participants_update_admin" on public.conversation_participants
  for update to authenticated
  using (public.is_conversation_participant_admin(conversation_id, auth.uid()))
  with check (public.is_conversation_participant_admin(conversation_id, auth.uid()));

-- -----------------------------------------------------------------------------
-- RLS policies: direct messages (participant-scoped reads/writes)
-- -----------------------------------------------------------------------------
drop policy if exists "direct_messages_participant_select" on public.direct_messages;
create policy "direct_messages_participant_select" on public.direct_messages
  for select to authenticated
  using (
    exists (
      select 1
      from public.conversation_participants cp
      where cp.conversation_id = direct_messages.conversation_id
        and cp.user_id = auth.uid()
        and cp.status = 'active'
    )
  );

drop policy if exists "direct_messages_participant_insert" on public.direct_messages;
create policy "direct_messages_participant_insert" on public.direct_messages
  for insert to authenticated
  with check (
    exists (
      select 1
      from public.conversation_participants cp
      where cp.conversation_id = new.conversation_id
        and cp.user_id = auth.uid()
        and cp.status = 'active'
    )
  );

-- -----------------------------------------------------------------------------
-- RLS policies: message reads (self read receipts only)
-- -----------------------------------------------------------------------------
drop policy if exists "message_reads_participant_select" on public.message_reads;
create policy "message_reads_participant_select" on public.message_reads
  for select to authenticated
  using (user_id = auth.uid());

drop policy if exists "message_reads_participant_insert" on public.message_reads;
create policy "message_reads_participant_insert" on public.message_reads
  for insert to authenticated
  with check (user_id = auth.uid());

drop policy if exists "message_reads_participant_update" on public.message_reads;
create policy "message_reads_participant_update" on public.message_reads
  for update to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- -----------------------------------------------------------------------------
-- RLS policies: notifications (own rows only; preserve existing behavior)
-- -----------------------------------------------------------------------------
drop policy if exists "notifications_own_select" on public.notifications;
create policy "notifications_own_select" on public.notifications
  for select to authenticated
  using (user_id = auth.uid());

drop policy if exists "notifications_own_insert" on public.notifications;
create policy "notifications_own_insert" on public.notifications
  for insert to authenticated
  with check (user_id = auth.uid());

drop policy if exists "notifications_own_update" on public.notifications;
create policy "notifications_own_update" on public.notifications
  for update to authenticated
  using (user_id = auth.uid());
