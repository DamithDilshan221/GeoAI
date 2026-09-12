from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import DataSource, FacilityStatus
from app.models.facility import Facility as FacilityORM
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository


def _seed_data(db_session: Session) -> tuple[int, list[int]]:
    cat_repo = CategoryRepository(db_session)
    c1 = cat_repo.create(code="restroom", label="Restroom")

    fac_repo = FacilityRepository(db_session)
    f1 = fac_repo.create(
        name="Facility 1",
        location_name="Building 1",
        category_id=c1.id,
        status=FacilityStatus.OPEN,
        latitude=10.0,
        longitude=20.0,
        data_source=DataSource.SYNTHETIC,
    )
    f2 = fac_repo.create(
        name="Facility 2",
        location_name="Building 2",
        category_id=c1.id,
        status=FacilityStatus.CLOSED,
        latitude=11.0,
        longitude=21.0,
        data_source=DataSource.SYNTHETIC,
    )
    f3 = fac_repo.create(
        name="Facility 3",
        location_name="Building 3",
        category_id=c1.id,
        status=FacilityStatus.OPEN,
        latitude=12.0,
        longitude=22.0,
        data_source=DataSource.SYNTHETIC,
    )

    # soft-delete f3
    row3 = db_session.query(FacilityORM).filter_by(id=f3.id).first()
    row3.is_active = False
    db_session.flush()

    return c1.id, [f1.id, f2.id, f3.id]


def test_list_facilities(client: TestClient, db_session: Session) -> None:
    _, fac_ids = _seed_data(db_session)

    response = client.get("/api/v1/facilities")
    assert response.status_code == 200
    data = response.json()

    # Should only return the 2 active ones
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["items"][0]["category"] == "restroom"
    assert data["items"][1]["category"] == "restroom"


def test_list_facilities_filtered_by_status(client: TestClient, db_session: Session) -> None:
    _seed_data(db_session)

    response = client.get("/api/v1/facilities?status=OPEN")
    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["status"] == "OPEN"


def test_list_facilities_missing_category(client: TestClient, db_session: Session) -> None:
    _seed_data(db_session)

    response = client.get("/api/v1/facilities?category=nonexistent")
    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 0
    assert data["total"] == 0


def test_list_facilities_pagination_limit(client: TestClient, db_session: Session) -> None:
    _seed_data(db_session)

    response = client.get("/api/v1/facilities?limit=51")
    assert response.status_code == 422


def test_get_facility(client: TestClient, db_session: Session) -> None:
    _, fac_ids = _seed_data(db_session)
    f1_id = fac_ids[0]

    response = client.get(f"/api/v1/facilities/{f1_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == f1_id
    assert data["category"] == "restroom"


def test_get_facility_not_found(client: TestClient, db_session: Session) -> None:
    response = client.get("/api/v1/facilities/999999999")
    assert response.status_code == 404


def test_get_facility_soft_deleted(client: TestClient, db_session: Session) -> None:
    _, fac_ids = _seed_data(db_session)
    f3_id = fac_ids[2]  # soft-deleted

    response = client.get(f"/api/v1/facilities/{f3_id}")
    assert response.status_code == 404
