# IITM BS Mentoring & Career Support Platform

The project contains the existing React/Vite frontend and a Flask backend that persists application data through Supabase only. Follow `backend/README.md` for Supabase setup and local startup.

## How to start

### Backend

The backend is started with the provided script `backend/start.sh`. It creates the virtual environment (if missing), installs dependencies, checks `backend/.env`, and starts Flask on port 5001.

```bash
cd backend
cp .env.example .env   # first run only — then fill in Supabase + OpenRouter credentials
chmod +x start.sh      # first run only
./start.sh             # or: bash start.sh
```

Backend runs at `http://localhost:5001` (health check: `GET /api/health`). See `backend/README.md` for Supabase setup details.

### Frontend

```bash
cd frontend
npm install   # first run only
npm run dev
```

Frontend runs at `http://localhost:5173` and talks to the backend at `http://localhost:5001/api` by default (`VITE_API_BASE_URL`, see `frontend/.env.example`).

### Demo logins

| Role | Email | Password |
|---|---|---|
| Student | `student@iitm.ac.in` | `student123` |
| Mentor | `mentor@iitm.ac.in` | `mentor123` |
| Admin (IIC) | `admin@iitm.ac.in` | `admin123` |
