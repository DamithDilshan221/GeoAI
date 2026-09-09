import pytest
from sqlalchemy import text

from app.domain.exceptions import FacilityNotFoundError
from app.models.enums import DataSource, FacilityStatus
from app.repositories.facility_repository import FacilityRepository
from app.repositories.usage_record_repository import UsageRecordRepository
from app.services.ml_inference_service import MLInferenceService


def seed_facility(session, name, category_id, capacity=None):
    from app.models.facility import Facility
    f = Facility(
        name=name, category_id=category_id, latitude=0.0, longitude=0.0,
        status=FacilityStatus.OPEN, capacity=capacity, data_source=DataSource.SYNTHETIC
    )
    session.add(f)
    session.flush()
    return f

def test_ml_inference_service_unknown_facility(db_session):
    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    service = MLInferenceService(db_session, usage_repo, facility_repo)

    with pytest.raises(FacilityNotFoundError):
        service.predict_usage(facility_id=999, day_of_week=2, hour=9)

def test_ml_inference_service_success(db_session):
    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    service = MLInferenceService(db_session, usage_repo, facility_repo)

    from app.models.category import Category
    c = Category(code="test_svc", label="Test Category Service")
    db_session.add(c)
    db_session.flush()
    f = seed_facility(db_session, "F_Service", c.id, capacity=20)

    # We rely on alembic having seeded ml_model_versions heuristic-v0
    res = service.predict_usage(facility_id=f.id, day_of_week=2, hour=9)
    assert res.source == "heuristic"
    assert res.confidence == "low"
    assert res.predicted_usage == 0.0

def test_ml_inference_service_no_active_provider(db_session):
    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    service = MLInferenceService(db_session, usage_repo, facility_repo)

    from app.models.category import Category
    c = Category(code="test_svc2", label="Test Category Service 2")
    db_session.add(c)
    db_session.flush()
    f = seed_facility(db_session, "F_Service2", c.id, capacity=20)

    # Temporarily set is_active=false to simulate missing provider
    db_session.execute(text("UPDATE ml_model_versions SET is_active = false"))
    db_session.flush()

    with pytest.raises(RuntimeError, match="No active row in ml_model_versions"):
        service.predict_usage(facility_id=f.id, day_of_week=2, hour=9)
