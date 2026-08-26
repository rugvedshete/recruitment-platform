# HireHub — Recruitment Platform

A full-stack job application platform where recruiters post jobs and manage
applicants, and candidates search for roles and track their applications —
built to demonstrate production-style software engineering practices: typed
frontend, tested backend, RBAC, containerized deployment, and CI.

> **Live demo:** not hosted (see [Deploying it yourself](#deploying-it-yourself) below
> for a one-command way to run it, or a free-tier deployment path).

## What problem does this solve?

Job boards need to serve two very different users from the same data: recruiters
who post and manage listings, and candidates who search and apply. That means
real authentication, real authorization (a recruiter shouldn't be able to edit
someone else's job posting), and a search experience that scales beyond a toy
dataset. This project implements that end to end rather than mocking it.

## What I built

- **Backend**: FastAPI REST API with JWT auth, role-based access control
  (candidate / recruiter / admin), full CRUD for job postings, an application
  workflow with status tracking, and search/filtering (free text, location,
  skill, employment type, salary range) with pagination.
- **Frontend**: React + TypeScript SPA (Vite) — job search/browse, job detail
  with an apply flow, a recruiter dashboard to post jobs and manage applicant
  status, and role-gated routing.
- **Database**: PostgreSQL, accessed via SQLAlchemy ORM.
- **Tests**: 21 backend tests (pytest) covering auth, RBAC, search/filter logic,
  and the full application workflow — run against an isolated in-memory DB.
- **Deployment**: Dockerfiles for both services + `docker-compose.yml`, wired
  with a Postgres health check so startup ordering is correct.
- **CI**: GitHub Actions pipeline — backend tests → frontend type-check/build →
  Docker image builds, on every push/PR.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full design rationale, data
model, and RBAC implementation details.

## Why this architecture?

FastAPI gives automatic request validation (Pydantic) and OpenAPI docs for
free, and its dependency-injection system makes "require this role" a
one-line, testable declaration rather than scattered `if` checks. JWTs keep
the backend stateless so it can scale horizontally without a session store.
PostgreSQL was chosen over a NoSQL option because the data is inherently
relational (users → jobs → applications, with foreign-key integrity that
matters — e.g. you can't apply to a job that doesn't exist). Full reasoning
in `ARCHITECTURE.md`.

## Technologies used

| Layer      | Technology |
|------------|------------|
| Frontend   | React 18, TypeScript, Vite, React Router, Axios |
| Backend    | Python 3.12, FastAPI, SQLAlchemy, Pydantic v2, python-jose (JWT), passlib (bcrypt) |
| Database   | PostgreSQL 16 |
| Testing    | Pytest, FastAPI TestClient, in-memory SQLite for test isolation |
| Deployment | Docker, docker-compose, nginx (serving the frontend build) |
| CI         | GitHub Actions |

## Results

- **21/21 backend tests passing**, covering authentication, authorization
  boundaries (e.g. a recruiter cannot edit another recruiter's job, a
  candidate cannot post a job, a candidate cannot apply twice), and every
  search/filter combination.
- Frontend passes strict TypeScript compilation (`tsc --build`) and produces a
  production bundle (~76 KB gzipped) via `vite build`.
- Full request lifecycle verified manually: register → login → post job (as
  recruiter) → search/filter it (as anonymous/candidate) → apply (as
  candidate) → view & update applicant status (as recruiter).

## How to run it

### Option A — Docker Compose (recommended, one command)

```bash
git clone <your-repo-url>
cd recruitment-platform
cp .env.example .env   # adjust SECRET_KEY for anything beyond local use
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs (Swagger UI): http://localhost:8000/docs
- Postgres: localhost:5432 (user/pass `postgres`/`postgres`, db `recruitment`)

### Option B — Run services locally without Docker

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/recruitment
export SECRET_KEY=dev-secret
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Running tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

### Deploying it yourself

Both images are self-contained and can be pushed to any container registry and
run on Render, Railway, Fly.io, or an EC2/VM with `docker-compose`. Point
`VITE_API_URL` (frontend build arg) at your deployed backend URL, and set a
strong `SECRET_KEY` and a managed Postgres connection string for `DATABASE_URL`.

## What would I improve next

- Alembic migrations instead of `create_all` on startup
- Refresh tokens + a revocation list for JWTs
- A proper tags table for skills instead of comma-separated strings
- Frontend component/e2e tests (Vitest + Playwright)
- Rate limiting on the login endpoint
- Postgres full-text search once listing volume grows

Full list with reasoning in [`ARCHITECTURE.md`](./ARCHITECTURE.md#next-steps--what-id-improve-with-more-time).

## Project structure

```
recruitment-platform/
├── backend/
│   ├── app/                # FastAPI application (see ARCHITECTURE.md)
│   ├── tests/               # pytest suite (21 tests)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/              # typed API client functions
│   │   ├── context/            # AuthContext (JWT session state)
│   │   ├── components/          # Navbar, JobCard, ProtectedRoute
│   │   └── pages/                 # Jobs, JobDetail, Login, Register, Dashboard, Applications
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
├── ARCHITECTURE.md
└── README.md
```
