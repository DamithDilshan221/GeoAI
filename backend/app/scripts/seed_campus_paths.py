"""Seed script for campus pedestrian network."""

import json
import logging
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.campus_path import CampusPath
from app.models.enums import DataSource, PathType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent.parent.parent / "database" / "seed" / "campus_paths_test_network.json"


def seed_campus_paths(session: Session) -> None:
    """Seed campus paths from JSON and generate routing topology."""
    if not SEED_FILE.exists():
        logger.error(f"Seed file not found: {SEED_FILE}")
        return

    # Check if paths already exist
    count = session.query(CampusPath).count()
    if count > 0:
        logger.info(f"Found {count} existing campus paths. Skipping seed.")
        return

    logger.info(f"Loading paths from {SEED_FILE}...")
    with open(SEED_FILE) as f:
        data = json.load(f)

    paths = []
    for item in data:
        path = CampusPath(
            id=item["id"],
            geom=f"SRID=4326;{item['geom']}",
            path_type=PathType(item["path_type"]),
            cost=item["cost"],
            reverse_cost=item["reverse_cost"],
            source=item.get("source"),
            target=item.get("target"),
            is_active=item.get("is_active", True),
            data_source=DataSource(item["data_source"]),
        )
        paths.append(path)

    session.add_all(paths)
    session.commit()
    logger.info(f"Inserted {len(paths)} campus paths.")

    # Create topology
    logger.info("Generating pgRouting topology...")
    session.execute(text("""
        DROP TABLE IF EXISTS campus_paths_vertices_pgr;
        CREATE TABLE campus_paths_vertices_pgr AS
        SELECT source AS id, ST_StartPoint(geom) AS the_geom FROM campus_paths
        UNION
        SELECT target AS id, ST_EndPoint(geom) AS the_geom FROM campus_paths;
        CREATE INDEX idx_campus_paths_vertices_pgr_id ON campus_paths_vertices_pgr (id);
    """))
    session.commit()
    logger.info("Topology generation complete.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_campus_paths(db)
    finally:
        db.close()
