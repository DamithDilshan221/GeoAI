import pytest
from fastapi.testclient import TestClient

from app.models.campus_path import CampusPath
from app.models.enums import DataSource, FacilityStatus, PathType
from app.models.facility import Facility
from app.scripts.seed_campus_paths import SEED_FILE


@pytest.fixture
def test_network_and_facility(db_session):
    # Seed the test network manually for isolation
    import json

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

    db_session.add_all(paths)

    from app.models.category import Category

    cat = Category(id=1, code="TEST", label="Test Cat", is_active=True)
    db_session.add(cat)
    db_session.commit()

    # Create a destination facility
    fac = Facility(
        id=999,
        name="Routing Target",
        category_id=1,
        status=FacilityStatus.OPEN,
        latitude=80.0,
        longitude=60.0,  # Corresponds to (60 80) in the test network
        geom="SRID=4326;POINT(60 80)",
        is_active=True,
        data_source=DataSource.SYNTHETIC,
    )
    db_session.add(fac)
    db_session.commit()

    # Create topology table manually since pgr_createTopology is removed in pgRouting 4.0
    from sqlalchemy import text

    db_session.execute(text("CREATE EXTENSION IF NOT EXISTS pgrouting;"))
    db_session.commit()
    db_session.execute(
        text("""
        DROP TABLE IF EXISTS campus_paths_vertices_pgr;
        CREATE TABLE campus_paths_vertices_pgr AS
        SELECT source AS id, ST_StartPoint(geom) AS the_geom FROM campus_paths
        UNION
        SELECT target AS id, ST_EndPoint(geom) AS the_geom FROM campus_paths;
        CREATE INDEX idx_campus_paths_vertices_pgr_id ON campus_paths_vertices_pgr (id);
    """)
    )
    db_session.commit()

    return fac


def test_routing_endpoint_success(client: TestClient, test_network_and_facility):
    # Origin at (0 0), target facility is at (60 80)
    response = client.get("/api/v1/routes?lat=0.0&lon=0.0&facility_id=999")
    assert response.status_code == 200

    data = response.json()
    assert data["source"] == "network"
    assert "distance_m" in data
    assert "estimated_time_s" in data
    assert len(data["path"]) > 0


def test_routing_endpoint_facility_not_found(client: TestClient):
    response = client.get("/api/v1/routes?lat=0.0&lon=0.0&facility_id=99999")
    assert response.status_code == 404
