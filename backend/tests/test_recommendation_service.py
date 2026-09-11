"""Integration tests for RecommendationService against geoai_test."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.domain.gis.nearby_search_service import NearbySearchService
from app.domain.routing.pedestrian_routing_service import PedestrianRoutingService
from app.models.enums import AudienceType, DataSource, FacilityStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.gis_repository import GISRepository
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

    return RecommendationService(
        nearby_search=nearby,
        routing_service=routing,
        ml_service=ml,
        facility_repo=fac_repo,
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
    assert result.message == "No suitable facilities were found within the current search radius."
    assert result.explanation is None


def test_staff_preferred_affects_suitability(db_session: Session) -> None:
    """staff_preferred preference boosts STAFF facility's suitability score."""
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

    # Both return results
    assert len(result_no_pref.ranked_facilities) == 2
    assert len(result_staff.ranked_facilities) == 2

    # f1 is VISITOR — should have suitability penalty under staff_preferred
    f1_no_pref = next(
        s for s in result_no_pref.ranked_facilities if s.candidate.facility.id == data["f1"].id
    )
    f1_staff = next(
        s for s in result_staff.ranked_facilities if s.candidate.facility.id == data["f1"].id
    )

    assert f1_no_pref.sub_scores["suitability"] == 100.0
    assert f1_staff.sub_scores["suitability"] == 20.0
