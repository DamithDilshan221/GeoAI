"""API integration tests for GET /api/v1/recommendations against geoai_test."""

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.enums import AudienceType, DataSource, FacilityStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository


def _seed_api_data(db_session: Session) -> dict:
    cat_repo = CategoryRepository(db_session)
    fac_repo = FacilityRepository(db_session)

    cat = cat_repo.create(code="api_test", label="API Test")

    f1 = fac_repo.create(
        name="API Close",
        location_name="Block C",
        category_id=cat.id,
        latitude=10.001,
        longitude=20.0,
        audience=AudienceType.VISITOR,
        status=FacilityStatus.OPEN,
        rating=4.0,
        data_source=DataSource.SYNTHETIC,
    )
    f2 = fac_repo.create(
        name="API Far",
        location_name="Block D",
        category_id=cat.id,
        latitude=10.004,
        longitude=20.0,
        audience=AudienceType.VISITOR,
        status=FacilityStatus.OPEN,
        rating=3.5,
        data_source=DataSource.SYNTHETIC,
    )

    return {"cat": cat, "f1": f1, "f2": f2}


def test_recommendations_api_success(client: TestClient, db_session: Session) -> None:
    _seed_api_data(db_session)

    resp = client.get("/api/v1/recommendations?lat=10.0&lon=20.0&category=api_test&radius_m=2000")
    assert resp.status_code == 200

    body = resp.json()
    assert body["message"] is None
    assert body["explanation"] is not None
    assert body["recommended_facility"] is not None
    assert body["recommended_facility"]["rank_position"] == 1
    assert len(body["ranked_facilities"]) == 2

    # First ranked should be the closer facility
    assert body["ranked_facilities"][0]["name"] == "API Close"
    assert body["ranked_facilities"][0]["rank_position"] == 1
    assert body["ranked_facilities"][1]["rank_position"] == 2

    # Verify sub-fields exist
    top = body["recommended_facility"]
    assert "recommendation_score" in top
    assert "crowd_level" in top
    assert "travel_source" in top
    assert "prediction_source" in top
    # Phase 11: lat/lon must be present for frontend navigation wiring
    assert "latitude" in top
    assert "longitude" in top


def test_recommendations_api_empty(client: TestClient, db_session: Session) -> None:
    resp = client.get(
        "/api/v1/recommendations?lat=10.0&lon=20.0&category=no_such_cat&radius_m=1000"
    )
    assert resp.status_code == 200

    body = resp.json()
    expected_msg = "No suitable washrooms were found within the current search radius."  # §22.1
    assert body["message"] == expected_msg
    assert body["explanation"] is None


def test_recommendations_api_staff_preferred(client: TestClient, db_session: Session) -> None:
    """staff_preferred narrows results to STAFF audience only."""
    cat_repo = CategoryRepository(db_session)
    fac_repo = FacilityRepository(db_session)

    cat = cat_repo.create(code="staff_test", label="Staff Test")
    fac_repo.create(
        name="Staff WC",
        location_name="Staff Block",
        category_id=cat.id,
        latitude=10.001,
        longitude=20.0,
        audience=AudienceType.STAFF,
        status=FacilityStatus.OPEN,
        data_source=DataSource.SYNTHETIC,
    )

    resp = client.get(
        "/api/v1/recommendations?lat=10.0&lon=20.0&category=staff_test&radius_m=2000"
        "&secondary_preference=staff_preferred"
    )
    assert resp.status_code == 200

    body = resp.json()
    assert len(body["ranked_facilities"]) == 1
    assert body["ranked_facilities"][0]["name"] == "Staff WC"


def test_recommendations_api_missing_params(client: TestClient) -> None:
    resp = client.get("/api/v1/recommendations?lat=10.0&lon=20.0")
    assert resp.status_code == 422  # missing category


def test_recommendations_api_writes_log_rows(client: TestClient, db_session: Session) -> None:
    """A successful API call must persist one log row per ranked facility."""
    _seed_api_data(db_session)

    resp = client.get("/api/v1/recommendations?lat=10.0&lon=20.0&category=api_test&radius_m=2000")
    assert resp.status_code == 200

    body = resp.json()
    expected_count = len(body["ranked_facilities"])
    assert expected_count > 0

    # Give the request-scoped session time to commit; then query via the test session.
    count = db_session.execute(
        text("SELECT COUNT(*) FROM recommendation_logs")
    ).scalar()
    assert count == expected_count

