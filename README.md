# GeoAI — Intelligent Facility Finder & Smart Navigation Recommendation System

GeoAI is a location-aware web application that helps users discover nearby facilities (hospitals, schools, banks, parks, etc.) and provides smart, personalized navigation recommendations powered by machine learning. The system combines spatial search with usage-pattern analysis to surface the most relevant facilities — not just the closest ones.

## Tech Stack

| Layer        | Technology                                  |
| ------------ | ------------------------------------------- |
| Frontend     | React 18, TypeScript, Vite, Tailwind CSS v3 |
| Backend      | Python 3.11+, FastAPI, Pydantic v2          |
| Database     | PostgreSQL 16 + PostGIS 3.4                 |
| ORM          | SQLAlchemy 2.0 + GeoAlchemy2                |
| Migrations   | Alembic                                     |
| ML (future)  | scikit-learn, pandas (lives under `ml/`)    |
| Maps         | Google Maps JavaScript API (Phase 7+)       |
| Dev Tooling  | Ruff, ESLint, Prettier, Vitest, pytest      |

## Prerequisites

- **Git** — any recent version
- **Node.js 20+** and npm
- **Python 3.11+**
- **Docker Desktop** (for the PostGIS database)

## Getting Started

```bash
# 1. Clone the repo
git clone <repo-url> && cd GeoAI

# 2. Create your local .env from the template
cp .env.example .env          # adjust values if needed

# 3. Start the PostGIS database
docker compose up -d db
docker compose ps              # confirm status is "healthy"

# 4. Backend setup
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload  # → http://localhost:8000

# 5. Frontend setup (new terminal)
cd frontend
npm install
npm run dev                    # → http://localhost:5173

# 6. Verify
# Open http://localhost:5173 — the placeholder page should show
# "Backend: connected" when the backend is running.
# Visit http://localhost:8000/api/v1/health for the raw JSON check.
```

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
├── docker-compose.yml PostGIS service for local development
├── .env.example       Environment variable template
└── README.md          ← you are here
```

## Project Status

**Phase 1 of 20** — Project Foundation (scaffold, config, health check).  
See [`docs/architecture/`](docs/architecture/) for the full specification.
