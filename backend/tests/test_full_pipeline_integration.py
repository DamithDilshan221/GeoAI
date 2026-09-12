"""Task B — Cross-service backend integration tests.

Exercises the complete request pipeline:
GIS (PostGIS spatial lookup) -> Prediction (ML/Heuristic provider) ->
Recommendation (Scoring & Ranking) -> Routing (OSRM client) -> Logging (audit records)
against the real geoai_test database without mocking internal domain services.
"""

from datetime import UTC, date, datetime, timedelta
from unittest.mock import MagicMock, patch

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.gis.nearby_search_service import NearbySearchService
from app.domain.routing.pedestrian_routing_service import PedestrianRoutingService
from app.domain.usage_data.synthetic_generator import generate_synthetic_usage_count
from app.models.enums import AudienceType, DataSource, FacilityStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.gis_repository import GISRepository
from app.repositories.ml_model_version_repository import MLModelVersionRepository
from app.repositories.recommendation_log_repository import RecommendationLogRepository
from app.repositories.usage_record_repository import UsageRecordRepository
from app.services.ml_inference_service import MLInferenceService
from app.services.recommendation_service import RecommendationResult, RecommendationService


def _seed_pipeline_data(db_session: Session) -> dict:
    """Seed category, 3 washrooms of varying audience, and synthetic usage history."""
    cat_repo = CategoryRepository(db_session)
    fac_repo = FacilityRepository(db_session)
    usage_repo = UsageRecordRepository(db_session)

    cat = cat_repo.create(code="full_pipeline_cat", label="Full Pipeline Category")

    # Seed 3 facilities near campus reference point (7.2545, 80.5965)
    f1 = fac_repo.create(
        name="Campus Center WC",
        location_name="Main Quad Building 1",
        category_id=cat.id,
        latitude=7.2550,
        longitude=80.5970,
        audience=AudienceType.VISITOR,
        status=FacilityStatus.OPEN,
        rating=4.8,
        fixtures={"normal": 4, "attached": 2},
        data_source=DataSource.SYNTHETIC,
    )
    f2 = fac_repo.create(
        name="Faculty Staff Restroom",
        location_name="Staff Complex B",
        category_id=cat.id,
        latitude=7.2560,
        longitude=80.5980,
        audience=AudienceType.STAFF,
        status=FacilityStatus.OPEN,
        rating=4.2,
        fixtures={"normal": 2, "attached": 1},
        data_source=DataSource.SYNTHETIC,
    )
    f3 = fac_repo.create(
        name="Distant Library Restroom",
        location_name="East Campus Annex",
        category_id=cat.id,
        latitude=7.2590,
        longitude=80.6010,
        audience=AudienceType.VISITOR,
        status=FacilityStatus.OPEN,
        rating=3.5,
        fixtures={"normal": 1},
        data_source=DataSource.SYNTHETIC,
    )

    # Seed 7 days of real usage records for all facilities
    today = date.today()
    for fac in [f1, f2, f3]:
        for day_offset in range(7):
            d = today - timedelta(days=day_offset)
            dow = d.weekday()
            for h in range(8, 20):
                cnt = generate_synthetic_usage_count(
                    facility_id=fac.id,
                    total_stalls=fac.total_stalls,
                    audience=fac.audience,
                    target_date=d,
                    hour=h,
                )
                usage_repo.upsert_hourly_record(
                    facility_id=fac.id,
                    record_date=d,
                    hour=h,
                    day_of_week=dow,
                    usage_count=cnt,
                    data_source=DataSource.SYNTHETIC,
                )

    db_session.flush()
    return {"cat": cat, "f1": f1, "f2": f2, "f3": f3}


def _build_full_service(db_session: Session) -> RecommendationService:
    """Build fully wired RecommendationService using real database repositories."""
    cat_repo = CategoryRepository(db_session)
    fac_repo = FacilityRepository(db_session)
    gis_repo = GISRepository(db_session)
    usage_repo = UsageRecordRepository(db_session)
    log_repo = RecommendationLogRepository(db_session)
    model_version_repo = MLModelVersionRepository(db_session)

    nearby = NearbySearchService(gis_repo, cat_repo)
    routing = PedestrianRoutingService(
        facility_repo=fac_repo,
        osrm_base_url="https://router.project-osrm.org",
        walking_speed_mps=1.2,
    )
    ml_service = MLInferenceService(
        session=db_session,
        usage_repo=usage_repo,
        facility_repo=fac_repo,
        category_repo=cat_repo,
        model_version_repo=model_version_repo,
    )

    return RecommendationService(
        nearby_search=nearby,
        routing_service=routing,
        ml_service=ml_service,
        facility_repo=fac_repo,
        log_repo=log_repo,
        model_version_repo=model_version_repo,
    )


def test_full_pipeline_recommendation_and_audit_logging(db_session: Session) -> None:
    """End-to-end integration across GIS, routing, prediction, recommendation and DB logging."""
    seed = _seed_pipeline_data(db_session)
    rec_service = _build_full_service(db_session)

    user_lat = 7.2545
    user_lon = 80.5965
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=UTC)

    # Mock OSRM network response per Phase 12's standard mocking pattern
    def fake_osrm_get(url: str, **kwargs):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 200
        # Return realistic walking route coordinates and duration
        resp.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 120.0,
                    "duration": 100.0,
                    "geometry": {
                        "coordinates": [[80.5965, 7.2545], [80.5970, 7.2550]],
                        "type": "LineString",
                    },
                    "legs": [{"steps": []}],
                }
            ],
        }
        return resp

    with patch("httpx.get", side_effect=fake_osrm_get):
        result = rec_service.get_recommendations(
            lat=user_lat,
            lon=user_lon,
            category_code=seed["cat"].code,
            radius_m=2000,
            limit=10,
            now=now,
        )

    # 1. Assert recommendation response structure
    assert isinstance(result, RecommendationResult)
    assert result.recommended_facility is not None
    assert len(result.ranked_facilities) == 3
    assert result.message is None

    # Top match should be the closest visitor washroom
    top = result.recommended_facility
    assert top.candidate.facility.id == seed["f1"].id
    assert top.candidate.distance_m > 0
    assert top.candidate.estimated_time_s > 0
    assert top.candidate.predicted_usage >= 0
    assert top.candidate.prediction_source in ("heuristic", "ml_model")
    assert top.final_score > 0

    # 2. Directly verify recommendation_logs audit table in geoai_test DB
    log_rows = db_session.execute(
        text(
            "SELECT request_id, facility_id, category_id, user_lat_rounded, user_lon_rounded, "
            "distance_m, predicted_usage, prediction_source, recommendation_score, rank_position, "
            "was_top_recommendation, model_version "
            "FROM recommendation_logs WHERE category_id = :cat_id "
            "ORDER BY rank_position ASC"
        ),
        {"cat_id": seed["cat"].id},
    ).fetchall()

    assert len(log_rows) == 3

    # All rows in the single recommendation request must share the exact same request_id
    request_ids = {r.request_id for r in log_rows}
    assert len(request_ids) == 1

    # Check top log row
    top_log = log_rows[0]
    assert top_log.facility_id == seed["f1"].id
    assert top_log.rank_position == 1
    assert top_log.was_top_recommendation is True
    assert float(top_log.user_lat_rounded) == round(user_lat, 3)
    assert float(top_log.user_lon_rounded) == round(user_lon, 3)
    assert top_log.prediction_source in ("heuristic", "ml_model")
    assert top_log.model_version is not None

    # Check non-top log rows
    assert log_rows[1].was_top_recommendation is False
    assert log_rows[1].rank_position == 2
    assert log_rows[2].was_top_recommendation is False
    assert log_rows[2].rank_position == 3


def test_full_pipeline_resilience_on_mid_pipeline_prediction_failure(
    db_session: Session,
) -> None:
    """When prediction encounters an error, recommendation degrades gracefully and logs."""
    seed = _seed_pipeline_data(db_session)
    rec_service = _build_full_service(db_session)

    user_lat = 7.2545
    user_lon = 80.5965
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=UTC)

    exploding_provider = MagicMock()
    exploding_provider.predict.side_effect = RuntimeError("Simulated ML engine crash")

    with patch(
        "app.services.ml_inference_service.get_active_provider",
        return_value=exploding_provider,
    ):
        result = rec_service.get_recommendations(
            lat=user_lat,
            lon=user_lon,
            category_code=seed["cat"].code,
            radius_m=2000,
            limit=10,
            now=now,
        )

    # Assert recommendation still completes end-to-end with graceful fallback
    assert result.recommended_facility is not None
    assert len(result.ranked_facilities) == 3

    top = result.recommended_facility
    assert top.candidate.prediction_source == "heuristic"
    assert top.candidate.predicted_usage == 0.0  # Graceful fallback default

    # Verify audit logs were still successfully recorded in the database
    log_count = db_session.execute(
        text("SELECT COUNT(*) FROM recommendation_logs WHERE category_id = :cat_id"),
        {"cat_id": seed["cat"].id},
    ).scalar()
    assert log_count == 3
