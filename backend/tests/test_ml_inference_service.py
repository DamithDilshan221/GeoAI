from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import text

from app.domain.exceptions import FacilityNotFoundError
from app.domain.ml_inference.provider import PredictionContext, PredictionResult
from app.models.enums import AudienceType, DataSource, FacilityStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.ml_model_version_repository import MLModelVersionRepository
from app.repositories.usage_record_repository import UsageRecordRepository
from app.services.ml_inference_service import MLInferenceService


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
    f = seed_facility(db_session, "F_Service", c.id, total_stalls=20, audience=AudienceType.VISITOR)

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
    f = seed_facility(
        db_session, "F_Service2", c.id, total_stalls=20, audience=AudienceType.VISITOR
    )

    # Temporarily set is_active=false to simulate missing provider
    db_session.execute(text("UPDATE ml_model_versions SET is_active = false"))
    db_session.flush()

    with pytest.raises(RuntimeError, match="No active row in ml_model_versions"):
        service.predict_usage(facility_id=f.id, day_of_week=2, hour=9)


# ── Phase 17 new tests ────────────────────────────────────────────────────────

def test_predict_usage_falls_back_to_heuristic_on_provider_exception_and_logs(
    db_session,
):
    """If the active provider raises during predict(), predict_usage() returns
    a heuristic PredictionResult -- not an exception -- and logs the failure.

    Logging is verified by patching ``logger.exception`` on the service module
    directly rather than relying on caplog propagation, which has proven
    unreliable with the current asyncio_mode=auto config.
    """
    import app.services.ml_inference_service as svc_module
    from app.models.category import Category

    c = Category(code="test_svc3", label="Test Category Service 3")
    db_session.add(c)
    db_session.flush()
    f = seed_facility(db_session, "F_Service3", c.id, total_stalls=20)

    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    category_repo = CategoryRepository(db_session)
    model_version_repo = MLModelVersionRepository(db_session)
    service = MLInferenceService(
        db_session, usage_repo, facility_repo, category_repo, model_version_repo
    )

    exploding_provider = MagicMock()
    exploding_provider.predict.side_effect = RuntimeError("simulated inference failure")

    with (
        patch.object(svc_module.logger, "exception") as mock_log,
        patch(
            "app.services.ml_inference_service.get_active_provider",
            return_value=exploding_provider,
        ),
    ):
        result = service.predict_usage(facility_id=f.id, day_of_week=2, hour=9)

    assert isinstance(result, PredictionResult)
    assert result.source == "heuristic"
    # The failure MUST have been logged (not silently swallowed).
    mock_log.assert_called_once()
    log_msg = mock_log.call_args[0][0]
    assert "Prediction failed for facility" in log_msg, (
        f"Expected 'Prediction failed for facility' in log message, got: {log_msg!r}"
    )


def test_predict_usage_falls_back_to_heuristic_on_provider_exception_caplog(db_session):
    """Verify fallback returns heuristic result when provider raises -- no log check.

    The logging assertion is covered by the companion test above.  This test
    re-confirms the fallback result shape with a different error message and
    category to rule out coincidental passing.
    """
    import app.services.ml_inference_service as svc_module
    from app.models.category import Category

    c = Category(code="test_svc4", label="Test Category Service 4")
    db_session.add(c)
    db_session.flush()
    f = seed_facility(db_session, "F_Service4", c.id, total_stalls=20)

    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    category_repo = CategoryRepository(db_session)
    model_version_repo = MLModelVersionRepository(db_session)
    service = MLInferenceService(
        db_session, usage_repo, facility_repo, category_repo, model_version_repo
    )

    exploding_provider = MagicMock()
    exploding_provider.predict.side_effect = ValueError("different error type")

    with (
        patch.object(svc_module.logger, "exception"),
        patch(
            "app.services.ml_inference_service.get_active_provider",
            return_value=exploding_provider,
        ),
    ):
        result = service.predict_usage(facility_id=f.id, day_of_week=2, hour=9)

    assert isinstance(result, PredictionResult)
    assert result.source == "heuristic"
    # crowd_level and confidence must be valid strings
    assert result.confidence in ("low", "medium", "high")
    assert result.predicted_usage >= 0.0


def test_category_code_resolved_and_passed_to_provider(db_session):
    """category_code must be correctly resolved and present in the
    PredictionContext passed to the provider's predict() method."""
    from app.models.category import Category

    c = Category(code="restroom", label="Restroom Category")
    db_session.add(c)
    db_session.flush()
    f = seed_facility(db_session, "F_Service5", c.id, total_stalls=20)

    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    category_repo = CategoryRepository(db_session)
    model_version_repo = MLModelVersionRepository(db_session)
    service = MLInferenceService(
        db_session, usage_repo, facility_repo, category_repo, model_version_repo
    )

    # Capture what PredictionContext was passed to provider.predict()
    captured_contexts = []

    def fake_predict(context: PredictionContext) -> PredictionResult:
        captured_contexts.append(context)
        return PredictionResult(
            predicted_usage=0.0,
            crowd_level="LOW",
            source="heuristic",
            confidence="low",
        )

    spy_provider = MagicMock()
    spy_provider.predict.side_effect = fake_predict

    with patch(
        "app.services.ml_inference_service.get_active_provider",
        return_value=spy_provider,
    ):
        service.predict_usage(facility_id=f.id, day_of_week=2, hour=9)

    assert len(captured_contexts) == 1
    ctx = captured_contexts[0]
    assert ctx.category_code == "restroom", (
        f"Expected category_code='restroom', got '{ctx.category_code}'"
    )
