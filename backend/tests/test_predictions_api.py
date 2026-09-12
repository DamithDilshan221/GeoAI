from app.models.enums import AudienceType, DataSource, FacilityStatus


def seed_facility(session, name, category_id, total_stalls=20, audience=AudienceType.VISITOR):
    from app.models.facility import Facility

    f = Facility(
        name=name,
        location_name=f"{name} Location",
        category_id=category_id,
        latitude=0.0,
        longitude=0.0,
        status=FacilityStatus.OPEN,
        audience=audience,
        fixtures={"normal": total_stalls} if total_stalls else {},
        data_source=DataSource.SYNTHETIC,
    )
    session.add(f)
    session.flush()
    return f


def test_predict_usage_success(client, db_session):
    from app.models.category import Category

    c = Category(code="cat_api", label="Cat API")
    db_session.add(c)
    db_session.flush()

    f = seed_facility(db_session, "F_API", c.id, total_stalls=20, audience=AudienceType.VISITOR)
    db_session.commit()  # commit data so client session can see it

    response = client.post(
        "/api/v1/predictions/usage", json={"facility_id": f.id, "day_of_week": 2, "hour": 9}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["facility_id"] == f.id
    assert "predicted_usage" in data
    assert data["source"] == "heuristic"
    assert data["confidence"] == "low"


def test_predict_usage_invalid_day(client):
    response = client.post(
        "/api/v1/predictions/usage", json={"facility_id": 1, "day_of_week": 7, "hour": 9}
    )
    assert response.status_code == 422


def test_predict_usage_not_found(client):
    response = client.post(
        "/api/v1/predictions/usage", json={"facility_id": 99999, "day_of_week": 2, "hour": 9}
    )
    assert response.status_code == 404


def test_health_prediction_provider(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "prediction_provider" in data
    assert data["prediction_provider"]["version"] == "heuristic-v0"
    assert data["prediction_provider"]["algorithm"] is None
