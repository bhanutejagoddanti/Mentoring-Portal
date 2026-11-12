-- =============================================================================
-- IITM BS Mentoring Portal - Migration 001: Help & Community Approval
-- Safe to run repeatedly (IF NOT EXISTS). Does not drop existing data.
-- =============================================================================

create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- -----------------------------------------------------------------------------
-- Help management
-- -----------------------------------------------------------------------------
create table if not exists public.help_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.user_profiles(id) on delete set null,
  user_name text,
  user_email text,
  role text check (role in ('student', 'mentor', 'admin')),
  ticket_type text not null,
  category text,
  priority text not null default 'Medium' check (priority in ('Low', 'Medium', 'High', 'Urgent')),
  description text not null,
  current_mentor text,
  reason_change text,
  urgency text,
  student_involved text,
  incident_category text,
  incident_date date,
  confidential boolean not null default false,
  status text not null default 'Submitted' check (status in ('Submitted','Under Review','Additional Information Required','Approved','Rejected','Resolved','Closed')),
  assigned_admin uuid references public.user_profiles(id) on delete set null,
  assigned_admin_name text,
  decision text,
  resolution_notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.help_request_messages (
  id uuid primary key default gen_random_uuid(),
  help_request_id uuid references public.help_requests(id) on delete cascade,
  legacy_ticket_id bigint,
  sender_id uuid references public.user_profiles(id) on delete set null,
  sender_name text,
  sender_role text,
  message text not null,
  is_internal boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.help_request_attachments (
  id uuid primary key default gen_random_uuid(),
  help_request_id uuid references public.help_requests(id) on delete cascade,
  file_name text not null,
  file_url text,
  mime_type text,
  file_size integer,
  uploaded_by uuid references public.user_profiles(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.intervention_logs (
  id uuid primary key default gen_random_uuid(),
  help_request_id uuid references public.help_requests(id) on delete cascade,
  legacy_ticket_id bigint,
  action text,
  performed_by uuid references public.user_profiles(id) on delete set null,
  performed_by_name text,
  notes text,
  decision text,
  resolution text,
  performed_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Community creation approval
-- -----------------------------------------------------------------------------
create table if not exists public.community_requests (
  id uuid primary key default gen_random_uuid(),
  requester_id uuid references public.user_profiles(id) on delete set null,
  requester_name text,
  requester_role text check (requester_role in ('student', 'mentor', 'admin')),
  community_name text not null,
  description text,
  category text default 'General',
  purpose text,
  target_audience text,
  community_type text default 'Discussion',
  reason text,
  suggested_moderators text[] default '{}',
  supporting_info text,
  status text not null default 'Pending' check (status in ('Pending','Approved','Rejected','Archived')),
  reviewed_by uuid references public.user_profiles(id) on delete set null,
  reviewed_by_name text,
  reviewed_at timestamptz,
  rejection_reason text,
  moderation_note text,
  created_community_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.community_request_reviews (
  id uuid primary key default gen_random_uuid(),
  community_request_id uuid references public.community_requests(id) on delete cascade,
  decision text check (decision in ('Approved','Rejected','Requested Changes')),
  reason text,
  reviewed_by uuid references public.user_profiles(id) on delete set null,
  reviewed_by_name text,
  reviewed_at timestamptz not null default now(),
  created_community_id uuid,
  created_at timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Backward-compatible column additions (no-op when columns already exist).
-- The base schema may have created older versions of these tables; add any
-- migration-intended columns before indexes / policies reference them.
-- -----------------------------------------------------------------------------
alter table public.help_requests add column if not exists user_id uuid references public.user_profiles(id) on delete set null;
alter table public.help_requests add column if not exists user_name text;
alter table public.help_requests add column if not exists user_email text;
alter table public.help_requests add column if not exists role text check (role in ('student', 'mentor', 'admin'));
alter table public.help_requests add column if not exists ticket_type text not null;
alter table public.help_requests add column if not exists category text;
alter table public.help_requests add column if not exists priority text not null default 'Medium' check (priority in ('Low', 'Medium', 'High', 'Urgent'));
alter table public.help_requests add column if not exists description text not null;
alter table public.help_requests add column if not exists current_mentor text;
alter table public.help_requests add column if not exists reason_change text;
alter table public.help_requests add column if not exists urgency text;
alter table public.help_requests add column if not exists student_involved text;
alter table public.help_requests add column if not exists incident_category text;
alter table public.help_requests add column if not exists incident_date date;
alter table public.help_requests add column if not exists confidential boolean not null default false;
alter table public.help_requests add column if not exists status text not null default 'Submitted' check (status in ('Submitted','Under Review','Additional Information Required','Approved','Rejected','Resolved','Closed'));
alter table public.help_requests add column if not exists assigned_admin uuid references public.user_profiles(id) on delete set null;
alter table public.help_requests add column if not exists assigned_admin_name text;
alter table public.help_requests add column if not exists decision text;
alter table public.help_requests add column if not exists resolution_notes text;

alter table public.intervention_logs add column if not exists legacy_ticket_id bigint;
alter table public.intervention_logs add column if not exists action text;
alter table public.intervention_logs add column if not exists performed_by uuid references public.user_profiles(id) on delete set null;
alter table public.intervention_logs add column if not exists performed_by_name text;
alter table public.intervention_logs add column if not exists decision text;
alter table public.intervention_logs add column if not exists resolution text;
alter table public.intervention_logs add column if not exists performed_at timestamptz not null default now();

-- Index for admin filtering
create index if not exists idx_help_requests_status on public.help_requests(status);
create index if not exists idx_help_requests_category on public.help_requests(ticket_type);
create index if not exists idx_help_requests_priority on public.help_requests(priority);
create index if not exists idx_help_requests_created on public.help_requests(created_at desc);
create index if not exists idx_help_messages_req on public.help_request_messages(help_request_id);
create index if not exists idx_interventions_req on public.intervention_logs(help_request_id);
create index if not exists idx_community_requests_status on public.community_requests(status);
create index if not exists idx_community_requests_created on public.community_requests(created_at desc);

-- updated_at trigger helper
create or replace function public.set_updated_at() returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_help_requests_updated on public.help_requests;
create trigger trg_help_requests_updated before update on public.help_requests
for each row execute procedure public.set_updated_at();

drop trigger if exists trg_community_requests_updated on public.community_requests;
create trigger trg_community_requests_updated before update on public.community_requests
for each row execute procedure public.set_updated_at();

-- -----------------------------------------------------------------------------
-- RLS policies (defense-in-depth; API also enforces role checks)
-- -----------------------------------------------------------------------------
alter table public.help_requests enable row level security;
alter table public.help_request_messages enable row level security;
alter table public.help_request_attachments enable row level security;
alter table public.intervention_logs enable row level security;
alter table public.community_requests enable row level security;
alter table public.community_request_reviews enable row level security;

-- Permissive service-role full access (backend uses service role key)
do $$
declare t text;
begin
  foreach t in array array['help_requests','help_request_messages','help_request_attachments','intervention_logs','community_requests','community_request_reviews'] loop
    execute format('drop policy if exists "service_role_all" on public.%I', t);
    execute format('create policy "service_role_all" on public.%I for all using (true) with check (true)', t);
  end loop;
end $$;

-- Authenticated read: requester sees own, admins see all (via is_admin helper if exists, else role check)
create or replace function public.is_admin(uid uuid) returns boolean as $$
  select exists (select 1 from public.user_profiles where id = uid and role = 'admin');
$$ language sql security definer;

drop policy if exists "help_requests_select_own_or_admin" on public.help_requests;
create policy "help_requests_select_own_or_admin" on public.help_requests
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));

drop policy if exists "help_requests_insert_own" on public.help_requests;
create policy "help_requests_insert_own" on public.help_requests
  for insert with check (user_id = auth.uid() or public.is_admin(auth.uid()));

drop policy if exists "help_requests_update_admin" on public.help_requests;
create policy "help_requests_update_admin" on public.help_requests
  for update using (public.is_admin(auth.uid())) with check (public.is_admin(auth.uid()));

drop policy if exists "help_messages_select_own_or_admin" on public.help_request_messages;
create policy "help_messages_select_own_or_admin" on public.help_request_messages
  for select using (
    exists (select 1 from public.help_requests h where h.id = help_request_id and (h.user_id = auth.uid() or public.is_admin(auth.uid())))
  );

drop policy if exists "help_messages_insert_own_or_admin" on public.help_request_messages;
create policy "help_messages_insert_own_or_admin" on public.help_request_messages
  for insert with check (
    exists (select 1 from public.help_requests h where h.id = help_request_id and (h.user_id = auth.uid() or public.is_admin(auth.uid())))
  );

drop policy if exists "interventions_admin_only" on public.intervention_logs;
create policy "interventions_admin_only" on public.intervention_logs
  for all using (public.is_admin(auth.uid())) with check (public.is_admin(auth.uid()));

drop policy if exists "community_requests_select_own_or_admin" on public.community_requests;
create policy "community_requests_select_own_or_admin" on public.community_requests
  for select using (requester_id = auth.uid() or public.is_admin(auth.uid()));

drop policy if exists "community_requests_insert_own" on public.community_requests;
create policy "community_requests_insert_own" on public.community_requests
  for insert with check (requester_id = auth.uid() or public.is_admin(auth.uid()));

drop policy if exists "community_requests_update_admin" on public.community_requests;
create policy "community_requests_update_admin" on public.community_requests
  for update using (public.is_admin(auth.uid())) with check (public.is_admin(auth.uid()));

drop policy if exists "community_reviews_admin_only" on public.community_request_reviews;
create policy "community_reviews_admin_only" on public.community_request_reviews
  for all using (public.is_admin(auth.uid())) with check (public.is_admin(auth.uid()));

-- -----------------------------------------------------------------------------
-- Storage note: supporting documents for help / community requests should use
-- the existing 'mentoring-files' bucket with folder-per-ticket scoping:
--   help-requests/<ticket_id>/<filename>
--   community-requests/<request_id>/<filename>
-- Restrict bucket to signed-in users via Supabase Storage policies.
-- -----------------------------------------------------------------------------
