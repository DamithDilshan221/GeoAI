# Testing Coverage & Architecture Audit

**Project:** GeoAI / Pera Rest Nav — Campus Washroom Finder  
**Phase:** 18 (Testing Hardening)  
**Reference:** `docs/architecture/PeraRestNav_Technical_Architecture_Specification_v3.md` §22

---

## 1. Executive Summary

This document provides a concise, honest audit of test coverage across the six testing tiers following the v2→v3 architecture corrections (PostGIS + OSRM routing, Leaflet mapping, scikit-learn ML pipeline, versioned model persistence, and unified recommendation logging).

---

## 2. Testing Tiers & Coverage Audit

### Tier 1 — Unit (Pure Functions, No Database)
* **What's Covered:** Pure scoring heuristics (distance, travel time, crowd levels, freshness, audience suitability penalties), feature engineering transformations, coordinate validations, distance estimation formulas (Haversine), and synthetic usage curve generation.
* **Key Files:** `backend/tests/test_recommendation_scoring.py`, `backend/tests/test_feature_engineering.py`, `backend/tests/test_synthetic_usage_generator.py`, `backend/tests/test_distance_estimation.py`.
* **Deliberately Not Covered:** Edge mathematical calculations for coordinates outside Sri Lanka boundaries (system rejects coordinates outside valid ranges prior to computation via pydantic schemas).

### Tier 2 — Backend Integration (Real Postgres & PostGIS)
* **What's Covered:** Repository CRUD operations, PostGIS GIST spatial queries (`ST_DWithin`, `ST_Distance`), table constraints (generated columns, ratings check, single-active ML model partial index, foreign key cascades), and Alembic migration apply/downgrade cleanliness.
* **Key Files:** `backend/tests/test_schema.py`, `backend/tests/test_repositories.py`, `backend/tests/test_gis_repository.py`, `backend/tests/test_usage_record_repository.py`, `backend/tests/test_recommendation_log_repository.py`.
* **Deliberately Not Covered:** Live multi-threaded race conditions on database row locks (out of scope for MVP single-instance application scale).

### Tier 3 — ML Pipeline & Persistence
* **What's Covered:** Feature matrix preparation, dataset building, scikit-learn pipeline inference, version-keyed model loader caching (`_MODEL_CACHE`), dynamic model provider factory, fallback on missing/corrupt artifacts, and CLI model promotion.
* **Key Files:** `backend/tests/test_trained_model_provider.py`, `backend/tests/test_provider_factory.py`, `backend/tests/test_ml_inference_service.py`.
* **Deliberately Not Covered:** Automated hyperparameter tuning and distributed model registry tracking (MLflow/S3) — model artifacts are versioned locally via joblib and JSON manifests per §15.

### Tier 4 — Routing (OSRM) & GIS Integration
* **What's Covered:** Pedestrian routing via OSRM HTTP foot profile, polyline decoding, maneuver parsing, fallback to straight-line Haversine estimates on network timeout or empty routes, and API endpoint integration.
* **Key Files:** `backend/tests/test_pedestrian_routing_service.py`, `backend/tests/test_full_pipeline_integration.py`, `frontend/src/routing/osrmClient.test.ts`, `frontend/src/routing/maneuvers.test.ts`.
* **Deliberately Not Covered:** Real live network traffic to external public OSRM servers during automated test execution (tests mock HTTP responses to prevent flaky network failures).

### Tier 5 — Frontend Unit & Component Tests
* **What's Covered:** Category selection, nearby washroom listings, audience filtering chips, Leaflet map rendering with DivIcons, turn-by-turn navigation overlay, live GPS position updates, and error/empty states.
* **Key Files:** `frontend/src/pages/*.test.tsx`, `frontend/src/components/map/*.test.tsx`, `frontend/src/components/navigation/*.test.tsx`, `frontend/src/hooks/*.test.ts`.
* **Deliberately Not Covered:** Browser hardware WebGL rendering and custom map tile tile-server network loading (mocked via standard Leaflet jsdom test utilities).

### Tier 6 — End-to-End (E2E User Journey)
* **What's Covered:** Complete user flow in a real Chromium browser — category & audience chip selection, GPS coordinates simulation, nearby facility listing verification against seeded campus washrooms, facility detail sheet opening, navigation overlay activation, and AI recommendation generation.
* **Key Files:** `frontend/e2e/user-journey.spec.ts`, `frontend/playwright.config.ts`.
* **Deliberately Not Covered:** Automated server process management inside Playwright — tests execute against already running development backend (`localhost:8000`) and frontend (`localhost:5173`) servers.

---

## 3. Suite Health & Quality Gate Summary

| Suite | Status | Test Count | Pass Rate |
|---|---|---|---|
| **Backend Pytest** | Passed | 202 tests | 100% (202 / 202) |
| **Frontend Vitest** | Passed | 116 tests | 100% (116 / 116) |
| **Cross-Service Integration** | Passed | Included in backend suite | 100% (2 / 2) |
| **Linting & Types** | Clean | `ruff` (backend), `tsc` / `eslint` (frontend) | 0 errors |
