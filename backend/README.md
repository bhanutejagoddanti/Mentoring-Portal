# Supabase-only Flask backend

This version uses Supabase Auth for identity, Supabase Postgres (through the Supabase Python client) for application records, and Supabase Storage for files. It does **not** connect directly to Postgres using `DATABASE_URL`, SQLAlchemy, psycopg or a local database.

## 1. Supabase setup
1. Create/open your Supabase project.
2. Open **SQL Editor** and run `supabase_setup.sql`.
3. Open **Project Settings → API**. Copy the Project URL, publishable/anon key, and secret/service-role key.
4. Copy `.env.example` to `.env` and fill in the values. The service-role key must remain on the Flask server and must never be placed in the frontend `.env`.

## 2. Install and run
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env, then:
python app.py
```

Run the frontend separately with `npm install` and `npm run dev`. Its API base defaults to `http://localhost:5001/api`.

## 3. Authentication and roles
Registration creates the identity through Supabase Auth Admin and writes the role/profile to `user_profiles`. Login uses Supabase Auth password sign-in. Flask validates the Supabase access token on protected API routes. New mentor accounts are pending IIC approval; student accounts are approved at registration.

To create an admin, register a user, then change that user's `role` to `admin` and `approved` to `true` in `user_profiles` using the Supabase SQL editor. Do not expose the service-role key.

## 4. Where data is stored
- Supabase Auth: accounts and password authentication.
- `user_profiles`: user role, name and approval status.
- `app_state`: prototype workflow data (mentors, students, requests, term settings, meetings, tasks, tickets, communities and community messages) as JSONB.
- `mentoring-files` Storage bucket: private file uploads (bucket provisioned; add upload endpoints before enabling file upload UI).

## Important prototype limitation
The existing frontend uses a whole-state `/api/state` adapter. This keeps the supplied UI compatible, but a single JSONB document is not ideal for concurrent production traffic, fine-grained row-level security, or complex reporting. Before production, migrate each collection into normalized Supabase tables and use resource-specific APIs. The current mentor search ranks profile text stored in Supabase; this version does not yet create pgvector embeddings.

## Security
- Never commit `.env`.
- Never put `SUPABASE_SERVICE_ROLE_KEY` in Vite/browser code.
- Configure email/redirect settings and production CORS origins before deployment.
- Replace demo/sample data and add admin provisioning controls before production.
