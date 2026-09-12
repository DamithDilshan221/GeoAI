"""Integration tests for RecommendationService against geoai_test."""

from datetime import UTC, datetime
from unittest.mock import patch

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.gis.nearby_search_service import NearbySearchService
from app.domain.routing.pedestrian_routing_service import PedestrianRoutingService
from app.models.enums import AudienceType, DataSource, FacilityStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.gis_repository import GISRepository
from app.repositories.ml_model_version_repository import MLModelVersionRepository
from app.repositories.recommendation_log_repository import RecommendationLogRepository
from app.repositories.usage_record_repository import UsageRecordRepository
from app.services.ml_inference_service import MLInferenceService
from app.services.recommendation_service import RecommendationService


def _seed_recommendation_data(db_session: Session) -> dict:
    """Seed two facilities with known positions near (10.0, 20.0)."""
    cat_repo = CategoryRepository(db_session)
    fac_repo = FacilityRepository(db_session)

    cat = cat_repo.create(code="rec_test", label="Rec Test")

    f1 = fac_repo.create(
        name="Close Facility",
        location_name="Block A",
        category_id=cat.id,
        latitude=10.001,
        longitude=20.0,
        audience=AudienceType.VISITOR,
        status=FacilityStatus.OPEN,
        rating=4.5,
        data_source=DataSource.SYNTHETIC,
    )
    f2 = fac_repo.create(
        name="Far Facility",
        location_name="Block B",
        category_id=cat.id,
        latitude=10.005,
        longitude=20.0,
        audience=AudienceType.STAFF,
        status=FacilityStatus.OPEN,
        rating=3.0,
        data_source=DataSource.SYNTHETIC,
    )

    return {"cat": cat, "f1": f1, "f2": f2}


def _build_service(db_session: Session) -> RecommendationService:
    cat_repo = CategoryRepository(db_session)
    fac_repo = FacilityRepository(db_session)
    gis_repo = GISRepository(db_session)
    usage_repo = UsageRecordRepository(db_session)

    nearby = NearbySearchService(gis_repo, cat_repo)
    # Use a stub OSRM URL — the integration tests hit the DB but not OSRM;
    # the Haversine fallback fires automatically when OSRM is unreachable.
    routing = PedestrianRoutingService(
        facility_repo=fac_repo,
        osrm_base_url="http://localhost:5000",
        walking_speed_mps=1.2,
    )
    ml = MLInferenceService(db_session, usage_repo, fac_repo)
    log_repo = RecommendationLogRepository(db_session)
    model_version_repo = MLModelVersionRepository(db_session)

    return RecommendationService(
        nearby_search=nearby,
        routing_service=routing,
        ml_service=ml,
        facility_repo=fac_repo,
        log_repo=log_repo,
        model_version_repo=model_version_repo,
    )


def test_end_to_end_ranking(db_session: Session) -> None:
    """Closest facility should rank first."""
    data = _seed_recommendation_data(db_session)
    svc = _build_service(db_session)

    now = datetime.now(UTC)
    result = svc.get_recommendations(
        lat=10.0,
        lon=20.0,
        category_code="rec_test",
        radius_m=2000,
        limit=25,
        now=now,
    )

    assert result.message is None
    assert result.explanation is not None
    assert len(result.ranked_facilities) == 2
    assert result.recommended_facility is not None

    # Close Facility should rank higher
    assert result.recommended_facility.candidate.facility.id == data["f1"].id


def test_empty_result(db_session: Session) -> None:
    """Unknown category → empty result with message, not an error."""
    _seed_recommendation_data(db_session)
    svc = _build_service(db_session)

    result = svc.get_recommendations(
        lat=10.0,
        lon=20.0,
        category_code="nonexistent_category",
        radius_m=1000,
        limit=25,
    )

    assert result.recommended_facility is None
    assert result.ranked_facilities == []
    assert result.message == "No suitable washrooms were found within the current search radius."
    assert result.explanation is None


def test_staff_preferred_affects_suitability(db_session: Session) -> None:
    """staff_preferred narrows candidates to STAFF audience and gives full suitability.

    Under no preference: both VISITOR (f1) and STAFF (f2) are candidates.
    Under staff_preferred: only the STAFF facility (f2) is returned because
    find_nearby() filters by audience.  Within that single result, suitability
    score should be 100 (audience matches).
    """
    data = _seed_recommendation_data(db_session)
    svc = _build_service(db_session)

    now = datetime.now(UTC)

    result_no_pref = svc.get_recommendations(
        lat=10.0,
        lon=20.0,
        category_code="rec_test",
        radius_m=2000,
        limit=25,
        now=now,
    )
    result_staff = svc.get_recommendations(
        lat=10.0,
        lon=20.0,
        category_code="rec_test",
        radius_m=2000,
        limit=25,
        secondary_preference="staff_preferred",
        now=now,
    )

    # No preference → both facilities returned
    assert len(result_no_pref.ranked_facilities) == 2

    # staff_preferred → only the STAFF facility (f2) is returned
    assert len(result_staff.ranked_facilities) == 1
    assert result_staff.ranked_facilities[0].candidate.facility.id == data["f2"].id

    # Under no preference, f1 (VISITOR) gets full suitability (no preference active)
    f1_no_pref = next(
        s for s in result_no_pref.ranked_facilities if s.candidate.facility.id == data["f1"].id
    )
    assert f1_no_pref.sub_scores["suitability"] == 100.0

    # Under staff_preferred, f2 (STAFF) gets full suitability (audience matches)
    f2_staff = result_staff.ranked_facilities[0]
    assert f2_staff.sub_scores["suitability"] == 100.0


def test_logging_writes_rows_per_ranked_candidate(db_session: Session) -> None:
    """Each scored candidate produces exactly one recommendation_logs row.

    Verifies:
    - row count == len(ranked_facilities)
    - all rows share one request_id
    - exactly one row has was_top_recommendation = true, matching the top facility
    - model_version == 'heuristic-v0' (seeded by migration 0003)
    - stored lat/lon are the rounded versions of the call coordinates
    """
    data = _seed_recommendation_data(db_session)
    svc = _build_service(db_session)

    call_lat = 10.0
    call_lon = 20.0

    result = svc.get_recommendations(
        lat=call_lat,
        lon=call_lon,
        category_code="rec_test",
        radius_m=2000,
        limit=25,
    )
    assert result.recommended_facility is not None
    expected_count = len(result.ranked_facilities)

    # Read back all log rows written for this call
    rows = db_session.execute(
        text(
            "SELECT request_id, facility_id, user_lat_rounded, user_lon_rounded, "
            "rank_position, was_top_recommendation, model_version "
            "FROM recommendation_logs ORDER BY rank_position"
        )
    ).all()

    # One row per scored candidate
    assert len(rows) == expected_count

    # All rows share one request_id
    request_ids = {r.request_id for r in rows}
    assert len(request_ids) == 1

    # Exactly one was_top_recommendation = true
    top_rows = [r for r in rows if r.was_top_recommendation]
    assert len(top_rows) == 1
    assert top_rows[0].facility_id == result.recommended_facility.candidate.facility.id

    # model_version matches the seeded active version
    assert all(r.model_version == "heuristic-v0" for r in rows)

    # Stored coordinates are rounded to 3 decimal places
    expected_lat = round(call_lat, 3)
    expected_lon = round(call_lon, 3)
    assert all(float(r.user_lat_rounded) == expected_lat for r in rows)
    assert all(float(r.user_lon_rounded) == expected_lon for r in rows)

    _ = data  # suppress unused-variable warning


def test_logging_failure_does_not_affect_response(db_session: Session) -> None:
    """A log-write failure must not propagate — response is still returned normally.

    Resolved decision #5: best-effort logging.  Monkeypatches log_candidate to
    raise so there is no transient-network dependency for this test.
    """
    _seed_recommendation_data(db_session)
    svc = _build_service(db_session)

    with patch.object(svc._log_repo, "log_candidate", side_effect=Exception("DB exploded")):
        result = svc.get_recommendations(
            lat=10.0,
            lon=20.0,
            category_code="rec_test",
            radius_m=2000,
            limit=25,
        )

    # The recommendation result is unaffected despite the logging failure
    assert result.recommended_facility is not None
    assert len(result.ranked_facilities) == 2
    assert result.message is None
    assert result.explanation is not None

    # No rows should have been written (the patch raised before any flush)
    count = db_session.execute(
        text("SELECT COUNT(*) FROM recommendation_logs")
    ).scalar()
    assert count == 0
