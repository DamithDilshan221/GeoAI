"""Idempotent seed script for the GeoAI development database (spec §24.1).

Targets ``settings.DATABASE_URL`` (the DEV ``geoai`` database) — NOT the test
database.  Safe to re-run: categories are skipped if their code already exists,
and facilities are skipped if a facility with the same name already exists.

Run from the ``backend/`` directory with the virtualenv active::

    python -m app.scripts.seed_database

The entire operation is wrapped in a single transaction; any failure rolls
back cleanly so the database is never left in a half-seeded state.

Exit codes:
    0 — success (all rows inserted or already present)
    1 — fatal error (exception printed; transaction rolled back)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.models.enums import DataSource, FacilityStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.exceptions import DuplicateCategoryCodeError
from app.repositories.facility_repository import FacilityRepository

# Paths to seed data files — resolved relative to the repo root so the script
# works whether invoked from backend/ or the repo root.
# __file__ = backend/app/scripts/seed_database.py
# parents[0] = backend/app/scripts
# parents[1] = backend/app
# parents[2] = backend
# parents[3] = repo root (GeoAI)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_SEED_DIR = _REPO_ROOT / "database" / "seed"
_CATEGORIES_FILE = _SEED_DIR / "categories.json"
_FACILITIES_FILE = _SEED_DIR / "facilities.json"


def _load_json(path: Path) -> list[dict]:  # type: ignore[type-arg]
    """Read and parse a JSON file, raising a clear error on failure."""
    if not path.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)  # type: ignore[no-any-return]


def run_seed() -> None:
    """Execute the full seed operation against the dev database."""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL, echo=False)
    SessionFactory = sessionmaker(bind=engine)

    categories_data = _load_json(_CATEGORIES_FILE)
    facilities_data = _load_json(_FACILITIES_FILE)

    cat_inserted = 0
    cat_skipped = 0
    fac_inserted = 0
    fac_skipped = 0

    with SessionFactory() as session:
        try:
            cat_repo = CategoryRepository(session)
            fac_repo = FacilityRepository(session)

            # ── Phase 1: seed categories ─────────────────────────────────
            code_to_id: dict[str, int] = {}
            for entry in categories_data:
                code: str = entry["code"]
                label: str = entry["label"]

                existing = cat_repo.get_by_code(code)
                if existing is not None:
                    code_to_id[code] = existing.id
                    cat_skipped += 1
                    continue

                try:
                    created = cat_repo.create(code=code, label=label)
                    code_to_id[code] = created.id
                    cat_inserted += 1
                except DuplicateCategoryCodeError:
                    # Race condition guard — treat as already-present
                    row = cat_repo.get_by_code(code)
                    if row:
                        code_to_id[code] = row.id
                    cat_skipped += 1

            # ── Phase 2: seed facilities ──────────────────────────────────
            for entry in facilities_data:
                name: str = entry["name"]

                existing_fac = fac_repo._get_by_name(name)
                if existing_fac is not None:
                    fac_skipped += 1
                    continue

                cat_code: str = entry["category_code"]
                if cat_code not in code_to_id:
                    raise ValueError(
                        f"Facility '{name}' references unknown category code "
                        f"'{cat_code}' — check facilities.json"
                    )

                fac_repo.create(
                    name=name,
                    category_id=code_to_id[cat_code],
                    latitude=float(entry["latitude"]),
                    longitude=float(entry["longitude"]),
                    status=FacilityStatus(entry["status"]),
                    rating=float(entry["rating"]) if entry.get("rating") is not None else None,
                    capacity=entry.get("capacity"),
                    accessibility=entry.get("accessibility"),
                    data_source=DataSource(entry["data_source"]),
                )
                fac_inserted += 1

            session.commit()

        except Exception:
            session.rollback()
            raise

    total_skipped = cat_skipped + fac_skipped
    print(
        f"Inserted {cat_inserted} categories, {fac_inserted} facilities ({total_skipped} skipped)"
    )


if __name__ == "__main__":
    try:
        run_seed()
    except Exception as exc:  # noqa: BLE001
        print(f"Seed failed: {exc}", file=sys.stderr)
        sys.exit(1)
