# Architecture

## Overview

HireHub is a three-tier application: a React/TypeScript SPA talks to a stateless
FastAPI backend over a JSON REST API, which persists data in PostgreSQL.

```
┌─────────────────┐      HTTPS/JSON      ┌──────────────────┐      SQL      ┌──────────────┐
│  React + TS SPA │ ───────────────────▶ │  FastAPI backend │ ────────────▶ │  PostgreSQL  │
│  (nginx, :3000) │ ◀─────────────────── │     (:8000)      │ ◀──────────── │   (:5432)    │
└─────────────────┘      JWT bearer      └──────────────────┘               └──────────────┘
```

## Why this stack

- **FastAPI** over Django/Flask: async-ready, automatic OpenAPI docs, native Pydantic
  validation, and a dependency-injection system that makes RBAC and DB session
  management explicit and testable (`app/deps.py`).
- **PostgreSQL**: relational integrity for users/jobs/applications with foreign keys
  and enums; battle-tested for this kind of transactional workload.
- **React + TypeScript + Vite**: fast dev loop, static typing shared conceptually
  with the backend's Pydantic schemas (see `frontend/src/types.ts`), small bundle.
- **JWT (stateless auth)**: no server-side session store needed; scales horizontally;
  trade-off is that revoking a token before expiry requires a denylist (not
  implemented — see "Next steps").

## Backend structure

```
backend/app/
├── main.py         # FastAPI app, CORS, router wiring, startup DB init
├── config.py        # Environment-driven settings
├── database.py       # SQLAlchemy engine/session factory
├── models.py         # ORM models: User, Job, Application (+ enums)
├── schemas.py         # Pydantic request/response schemas
├── security.py         # Password hashing (bcrypt) + JWT encode/decode
├── deps.py               # get_current_user, require_roles(*roles) RBAC dependency
└── routers/
    ├── auth.py            # register / login / me
    ├── jobs.py             # CRUD + search & filtering
    └── applications.py      # apply, list mine, list for a job, update status
```

### Role-based access control

Three roles: `candidate`, `recruiter`, `admin`. RBAC is enforced with a single
reusable FastAPI dependency:

```python
def require_roles(*roles: Role):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(403, ...)
        return current_user
    return checker
```

Routers declare their own requirements, e.g. `Depends(require_roles(Role.recruiter, Role.admin))`.
Ownership checks (a recruiter can only edit/view applicants for jobs *they* posted,
unless they're an admin) are enforced inside the route handlers against `posted_by_id`.

### Search & filtering

`GET /jobs` builds a single SQLAlchemy query incrementally: free-text search
(`ilike` across title/company/description), location, skill substring match,
employment type, and salary-range overlap — all optional and composable, with
pagination (`page`, `page_size`) and a `total` count for the frontend.

## Data model

- **User** — email, hashed password, full name, role
- **Job** — title, company, description, location, skills (comma-separated string
  for simplicity — a proper tags table would be the production evolution),
  employment type, salary range, `posted_by` (FK to User)
- **Application** — links a candidate to a job, tracks status through a fixed
  state machine (`submitted → under_review → interview → rejected/hired`)

## Testing strategy

Backend tests (`pytest`, 21 tests) run against an isolated **in-memory SQLite**
database per test session (via `StaticPool` so all connections share the same
DB), overriding the `get_db` FastAPI dependency. This means tests are fast,
hermetic, and don't require a running Postgres instance — while still exercising
the full HTTP layer via `TestClient`. Coverage includes:

- Auth: registration, duplicate-email rejection, login success/failure, token validation
- Jobs: RBAC enforcement, search, filtering by location/skill/salary, ownership checks on edit/delete
- Applications: apply flow, duplicate-application prevention, candidate-only restriction, recruiter visibility scoped to their own jobs

The frontend is currently verified via `tsc --build` (strict type-checking) and
a production `vite build`; component/integration tests (e.g. React Testing
Library) are a natural next addition.

## Deployment

Each service is containerized independently:

- `backend/Dockerfile` — slim Python image running `uvicorn`
- `frontend/Dockerfile` — multi-stage build: Node builds static assets, nginx serves them
- `docker-compose.yml` — wires Postgres + backend + frontend with health checks
  so the backend waits for Postgres to be ready before starting

CI (`.github/workflows/ci.yml`) runs on every push/PR: backend tests → frontend
type-check & build → Docker image builds for both services, gated so a broken
build never reaches the "can this even be containerized" stage.

## Next steps / what I'd improve with more time

- Replace `Base.metadata.create_all` with **Alembic migrations** for real schema versioning
- Add a JWT **refresh token** + denylist so access can be revoked before expiry
- Normalize `skills` into a many-to-many tags table for proper filtering instead of substring match
- Add a `GET /jobs?mine=true` endpoint instead of the frontend filtering client-side
- Rate limiting on `/auth/login` to slow brute-force attempts
- Frontend component tests (Vitest + React Testing Library) and an e2e smoke test (Playwright)
- Full-text search (Postgres `tsvector` or a dedicated search index) once the job volume outgrows `ILIKE`
