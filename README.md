# GeoAI — Intelligent Facility Finder & Smart Navigation Recommendation System

GeoAI is a location-aware web application that helps users discover nearby facilities (hospitals, schools, banks, parks, etc.) and provides smart, personalized navigation recommendations powered by machine learning. The system combines spatial search with usage-pattern analysis to surface the most relevant facilities — not just the closest ones.

## Tech Stack

| Layer        | Technology                                  |
| ------------ | ------------------------------------------- |
| Frontend     | React 18, TypeScript, Vite, Tailwind CSS v3 |
| Backend      | Python 3.11+, FastAPI, Pydantic v2          |
| Database     | PostgreSQL 17.x + PostGIS (native Windows)  |
| ORM          | SQLAlchemy 2.0 + GeoAlchemy2                |
| Migrations   | Alembic                                     |
| ML (future)  | scikit-learn, pandas (lives under `ml/`)    |
| Maps         | Google Maps JavaScript API (Phase 7+)       |
| Dev Tooling  | Ruff, ESLint, Prettier, Vitest, pytest      |

## Prerequisites

- **Git** — any recent version
- **Node.js 20+** and npm
- **Python 3.11+**
- **PostgreSQL 17.x + PostGIS** — installed natively as a Windows service (see `docs/architecture/` for the one-time setup steps documented in Part 0.1)

## Getting Started

```powershell
# 1. Clone the repo
git clone <repo-url>
cd GeoAI

# 2. Create your local .env from the template
Copy-Item .env.example .env
# ⚠ IMPORTANT: Open .env and replace "changeme" with the actual postgres
#   password you chose during the one-time native PostgreSQL install.
#   Never commit a real password — .env is in .gitignore.

# 3. Confirm PostgreSQL is running (it was set up in Part 0.1)
Get-Service postgresql-x64-18
# Expected: Status = Running

# 4. Backend setup
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload        # → http://localhost:8000

# 5. Frontend setup (new terminal)
cd frontend
npm install
npm run dev                           # → http://localhost:5173

# 6. Verify
# Open http://localhost:5173 — the placeholder page should show
# "Backend: connected" when the backend is running.
# Visit http://localhost:8000/api/v1/health for the raw JSON check.
```

## Database

The project uses PostgreSQL with the PostGIS extension. Migrations are managed via Alembic.

To apply migrations:
```powershell
cd backend
alembic upgrade head
```

To run the database tests:
```powershell
cd backend
pytest tests/test_schema.py -v
```

## Seeding Local Data

After running migrations, populate the dev database with the synthetic seed dataset
(~4 categories, ~20 facilities near Colombo):

```powershell
cd backend
# Activate your virtualenv first
.venv\Scripts\Activate.ps1

# First run — inserts all rows
python -m app.scripts.seed_database
# Example output: Inserted 4 categories, 20 facilities (0 skipped)

# Re-running is safe — skips rows that already exist
python -m app.scripts.seed_database
# Example output: Inserted 0 categories, 0 facilities (24 skipped)

# Seed synthetic usage history (Phase 9)
python -m app.scripts.generate_usage_history
# Safe to re-run (upserts existing buckets).
```

> **Note:** The seed script targets the **dev** `geoai` database (from `DATABASE_URL` in `.env`),
> never the `geoai_test` database. Test data is managed automatically by `pytest` fixtures.

## Repository Structure

```
GeoAI/
├── frontend/          React + TypeScript SPA (Vite dev server)
├── backend/           FastAPI application (layered architecture)
│   ├── app/
│   │   ├── api/       Route definitions (versioned under v1/)
│   │   ├── schemas/   Pydantic request/response models
│   │   ├── services/  Business-logic orchestration
│   │   ├── domain/    Core domain logic (GIS, ML inference, recommendations)
│   │   ├── repositories/  Data-access layer (SQLAlchemy queries)
│   │   ├── models/    SQLAlchemy ORM models
│   │   └── core/      Config, logging, shared infrastructure
│   ├── alembic/       Database migration scripts
│   └── tests/         Backend unit & integration tests
├── ml/                Machine-learning training pipeline (Phase 15+)
├── data/              Raw & processed data files
├── database/          SQL init scripts & seed data
├── docs/              Architecture docs & specification
├── tests/e2e/         End-to-end tests (Phase 18)
├── geoai/future/      Placeholder for post-MVP features (spec §31)
├── .env.example       Environment variable template
└── README.md          ← you are here
```

## Project Status

**Phase 3 of 20** — Facility Data Layer (repositories, validation, seed data).
See [`docs/architecture/`](docs/architecture/) for the full specification.
