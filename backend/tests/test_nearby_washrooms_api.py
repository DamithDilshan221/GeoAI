from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import AudienceType, DataSource, FacilityStatus
from app.models.facility import Facility as FacilityORM
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository


def _seed_gis_data(db_session: Session) -> None:
    cat_repo = CategoryRepository(db_session)
    c_restroom = cat_repo.create(code="restroom", label="Restroom")
    c_atm = cat_repo.create(code="atm", label="ATM")

    fac_repo = FacilityRepository(db_session)
    # Origin: 10.0, 20.0. 1 degree of lat is ~111,320m. 0.001 degree is ~111.3m.

    # 1. Very close, OPEN, active (Should match) - Dist ~111m (Visitor)
    fac_repo.create(
        name="Close Restroom",
        category_id=c_restroom.id,
        status=FacilityStatus.OPEN,
        audience=AudienceType.VISITOR,
        fixtures={"sinks": 2},
        latitude=10.001,
        longitude=20.0,
        data_source=DataSource.SYNTHETIC,
    )
    # 1.b Close Staff Restroom
    fac_repo.create(
        name="Staff Restroom",
        category_id=c_restroom.id,
        status=FacilityStatus.OPEN,
        audience=AudienceType.STAFF,
        fixtures={"sinks": 1},
        latitude=10.001,
        longitude=20.0,
        data_source=DataSource.SYNTHETIC,
    )
    # 2. Far, OPEN, active (Outside 1000m radius) - Dist ~1113m
    fac_repo.create(
        name="Far Restroom",
        category_id=c_restroom.id,
        status=FacilityStatus.OPEN,
        latitude=10.01,
        longitude=20.0,
        data_source=DataSource.SYNTHETIC,
    )
    # 3. Close, CLOSED, active (Should NOT match due to status)
    fac_repo.create(
        name="Closed Restroom",
        category_id=c_restroom.id,
        status=FacilityStatus.CLOSED,
        latitude=10.002,
        longitude=20.0,
        data_source=DataSource.SYNTHETIC,
    )
    # 4. Close, OPEN, inactive (Should NOT match due to active status)
    f_inactive = fac_repo.create(
        name="Inactive Restroom",
        category_id=c_restroom.id,
        status=FacilityStatus.OPEN,
        latitude=10.0005,
        longitude=20.0,
        data_source=DataSource.SYNTHETIC,
    )
    row = db_session.query(FacilityORM).filter_by(id=f_inactive.id).first()
    row.is_active = False
    db_session.flush()

    # 5. Distance 0, OPEN, active, but wrong category (ATM)
    fac_repo.create(
        name="Origin ATM",
        category_id=c_atm.id,
        status=FacilityStatus.OPEN,
        latitude=10.0,
        longitude=20.0,
        data_source=DataSource.SYNTHETIC,
    )


def test_get_nearby_facilities(client: TestClient, db_session: Session):
    _seed_gis_data(db_session)

    # Search at 10.0, 20.0 with 1000m radius for 'restroom', default (no audience)
    response = client.get(
        "/api/v1/washrooms/nearby?lat=10.0&lon=20.0&category=restroom&radius_m=1000"
    )
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)  # Explicitly assert it's a bare list, not an envelope
    assert len(data) == 2

    # Verify fields on the first item
    item = next(i for i in data if i["name"] == "Close Restroom")
    assert item["category"] == "restroom"
    assert item["status"] == "OPEN"
    assert item["audience"] == "VISITOR"
    assert item["fixtures"] == {"sinks": 2}
    assert "location_name" not in item
    assert "total_stalls" not in item
    # distance should be ~111m, check magnitude
    assert 110 < item["distance_m"] < 113


def test_get_nearby_facilities_unknown_category(client: TestClient, db_session: Session):
    response = client.get("/api/v1/washrooms/nearby?lat=10.0&lon=20.0&category=unknown_code")
    assert response.status_code == 200
    assert response.json() == []


def test_get_nearby_facilities_missing_params(client: TestClient):
    response = client.get("/api/v1/washrooms/nearby?lat=10.0&lon=20.0")
    assert response.status_code == 422  # Missing category

    response = client.get("/api/v1/washrooms/nearby?category=restroom")
    assert response.status_code == 422  # Missing coordinates


def test_get_nearby_facilities_invalid_coordinates(client: TestClient):
    response = client.get("/api/v1/washrooms/nearby?lat=91.0&lon=20.0&category=restroom")
    assert response.status_code == 422
    assert "Latitude 91.0 is out of bounds" in str(response.json())


def test_get_nearby_facilities_invalid_limit_and_radius(client: TestClient):
    response = client.get("/api/v1/washrooms/nearby?lat=10.0&lon=20.0&category=restroom&limit=51")
    assert response.status_code == 422

    response = client.get(
        "/api/v1/washrooms/nearby?lat=10.0&lon=20.0&category=restroom&radius_m=10001"
    )
    assert response.status_code == 422


def test_get_nearby_facilities_audience_filter(client: TestClient, db_session: Session):
    _seed_gis_data(db_session)
    
    # Filter by visitor
    response = client.get(
        "/api/v1/washrooms/nearby?lat=10.0&lon=20.0&category=restroom&audience=visitor&radius_m=1000"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Close Restroom"
    
    # Filter by staff
    response = client.get(
        "/api/v1/washrooms/nearby?lat=10.0&lon=20.0&category=restroom&audience=staff&radius_m=1000"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Staff Restroom"
    
    # Invalid audience
    response = client.get(
        "/api/v1/washrooms/nearby?lat=10.0&lon=20.0&category=restroom&audience=stuff&radius_m=1000"
    )
    assert response.status_code == 422
