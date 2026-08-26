# HireHub — Recruitment Platform

A full-stack job application platform where recruiters post jobs and manage
applicants, and candidates search for roles and track their applications —
built to demonstrate production-style software engineering practices: typed
frontend, tested backend, RBAC, containerized deployment, and CI.

> **Live demo:** not hosted (see [How to run it](#how-to-run-it) below for a
> one-command way to run it locally, or [Deploying it yourself](#deploying-it-yourself)
> for a free-tier hosting path).

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
| Frontend   | React 18, TypeScript, Vite, React Router |
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

The fastest path is Docker — one command builds and starts the database,
backend, and frontend together. Pick your OS below.

### Prerequisites (both OSes)

You need the project files on your machine (clone this repo or download it
as a ZIP) and Docker installed.

---

### 🐧 Linux (Ubuntu)

**1. Install Docker:**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
```

**2. Let your user run Docker without `sudo`:**
```bash
sudo usermod -aG docker $USER
```
Then **restart your computer** — this is required for the permission change
to take effect.

**3. Verify it installed:**
```bash
docker --version
```

**4. Move into the project folder and create your env file:**
```bash
cd recruitment-platform
cp .env.example .env
```

**5. Start everything:**
```bash
docker compose up --build
```
First run downloads images and builds both services — a few minutes. You'll
know it's ready when you see:
```
backend-1  | INFO:     Application startup complete.
backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

**⚠️ Port 5432 already in use?** If you already have PostgreSQL installed
locally, you'll see `failed to bind host port 0.0.0.0:5432/tcp: address
already in use`. Fix: stop with `Ctrl+C` then `docker compose down`, open
`docker-compose.yml`, and under the `db` service change:
```yaml
    ports:
      - "5432:5432"
```
to:
```yaml
    ports:
      - "5433:5432"
```
Save and re-run `docker compose up --build`. (Only the host-facing port
changes — the backend still reaches the database internally over Docker's
network regardless of this number.)

---

### 🪟 Windows

**1. Install Docker Desktop** from
[docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
Accept the WSL2 (Windows Subsystem for Linux) prompt if shown — it's required
and set up automatically. Restart if asked.

**2. Start Docker Desktop** from the Start menu and wait for "Docker is
running" (whale icon in the system tray stops animating).

**3. Extract the project:** right-click the downloaded ZIP → **Extract All**.

**4. Create your env file:** copy `.env.example` in the project folder and
rename the copy to exactly `.env`. If you can't see file extensions to
confirm the rename worked, enable them via File Explorer → View → Show →
File name extensions.

**5. Open a terminal in the project folder:** in File Explorer, click the
address bar inside the `recruitment-platform` folder, type `cmd`, press
Enter.

**6. Start everything:**
```powershell
docker compose up --build
```
Same as Linux — watch for `Uvicorn running on http://0.0.0.0:8000`.

**⚠️ Port 5432 conflict?** Same fix as Linux: `Ctrl+C`, `docker compose down`,
edit `docker-compose.yml`'s `db` service port to `"5433:5432"`, save, re-run.

---

### Open the app (both OSes)

- Frontend: [http://localhost:3000](http://localhost:3000)
- API docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

### Stop it

`Ctrl+C` in the terminal running `docker compose up`. Restart later with
`docker compose up` (no `--build` needed unless you changed code) from
inside the project folder.

### Running tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

### Troubleshooting quick reference

| Symptom | Cause | Fix |
|---|---|---|
| `permission denied` running `docker` (Linux) | Group change hasn't applied yet | Restart your computer |
| `address already in use` on port 5432 | Local Postgres already using that port | Change host port to `5433` in `docker-compose.yml` |
| `Cannot connect to the Docker daemon` | Docker service isn't running | Linux: `sudo systemctl start docker`. Windows: open Docker Desktop |
| `git push` fails with "Password authentication is not supported" | GitHub disabled password auth for Git operations | Use a Personal Access Token as the password instead |
| Site loads but API calls fail | Backend container not healthy yet, or wrong `VITE_API_URL` | Check `docker compose up` logs; confirm `localhost:8000/docs` loads |

### Deploying it yourself

Both images are self-contained and can be pushed to any container registry
and run on Render, Railway, Fly.io, or a VM with `docker-compose`. Point
`VITE_API_URL` (frontend build arg) at your deployed backend URL, and set a
strong `SECRET_KEY` and a managed Postgres connection string for
`DATABASE_URL`.

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
