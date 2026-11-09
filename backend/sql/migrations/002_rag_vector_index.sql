-- =============================================================================
-- Migration 002: RAG mentor vectors + pgvector retrieval + search audit
-- Safe to run repeatedly (IF NOT EXISTS). No existing data is dropped.
-- Apply AFTER supabase_setup.sql (or standalone — creates missing tables).
-- =============================================================================

create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";
create extension if not exists vector;

-- Mentor profiles (AI analysis + embedding bookkeeping)
create table if not exists public.mentor_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.user_profiles(id) on delete cascade,
  title text, role text, field text, industry text,
  bio text, background text, linkedin text,
  mode text default 'Online',
  slots integer not null default 2,
  hours text default '3-5 hours',
  available boolean not null default true,
  ai_profile jsonb not null default '{}'::jsonb,
  profile_indexed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Precomputed mentor embeddings (1536-dim text-embedding-3-small)
create table if not exists public.mentor_vectors (
  id uuid primary key default gen_random_uuid(),
  mentor_id uuid not null unique references public.mentor_profiles(id) on delete cascade,
  embedding vector(1536),
  extracted_metadata jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create index if not exists idx_mentor_vectors_embedding
  on public.mentor_vectors using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index if not exists idx_mentor_vectors_metadata
  on public.mentor_vectors using gin (extracted_metadata);

-- Semantic search RPC (RAG retrieval): nearest mentors to a query embedding
create or replace function public.match_mentors(
  query_embedding vector(1536),
  match_count int default 5
) returns table (
  mentor_id uuid,
  mentor_name text,
  similarity float
) language plpgsql stable as $$
begin
  return query
  select mp.id as mentor_id, up.name as mentor_name,
         1 - (mv.embedding <=> query_embedding) as similarity
  from public.mentor_vectors mv
  join public.mentor_profiles mp on mp.id = mv.mentor_id
  join public.user_profiles up on up.id = mp.user_id
  where up.approved = true and up.active = true and mp.available = true
  order by mv.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Search audit log (student queries -> recommendation quality monitoring)
create table if not exists public.mentor_search_logs (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references public.user_profiles(id) on delete set null,
  query text not null,
  filters jsonb not null default '{}'::jsonb,
  result_count integer not null default 0,
  created_at timestamptz not null default now()
);

-- RLS: mentor_vectors/search logs are server-managed (service role); read-only for owners via app_state.
alter table public.mentor_profiles enable row level security;
alter table public.mentor_vectors enable row level security;
alter table public.mentor_search_logs enable row level security;

drop policy if exists "service_role_all" on public.mentor_profiles;
create policy "service_role_all" on public.mentor_profiles for all using (true) with check (true);
drop policy if exists "service_role_all" on public.mentor_vectors;
create policy "service_role_all" on public.mentor_vectors for all using (true) with check (true);
drop policy if exists "service_role_all" on public.mentor_search_logs;
create policy "service_role_all" on public.mentor_search_logs for all using (true) with check (true);
