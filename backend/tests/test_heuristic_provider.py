from datetime import date

from app.domain.ml_inference.heuristic_provider import HeuristicUsageProvider
from app.domain.ml_inference.provider import PredictionContext
from app.models.enums import AudienceType, DataSource, FacilityStatus
from app.repositories.facility_repository import FacilityRepository
from app.repositories.usage_record_repository import UsageRecordRepository


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


def test_heuristic_provider_tier1_medium(db_session):
    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)

    # Needs a category first
    from app.models.category import Category

    c = Category(code="test_cat", label="Test Category")
    db_session.add(c)
    db_session.flush()

    f = seed_facility(db_session, "F1", c.id, total_stalls=20, audience=AudienceType.VISITOR)

    # 3 rows, mean = 6.0
    for i, count in enumerate([4, 6, 8]):
        usage_repo.upsert_hourly_record(
            facility_id=f.id,
            record_date=date(2026, 9, 1 + i),
            hour=9,
            day_of_week=2,
            usage_count=count,
            data_source=DataSource.SYNTHETIC,
        )

    provider = HeuristicUsageProvider(usage_repo, facility_repo)
    ctx = PredictionContext(
        facility_id=f.id,
        category_id=c.id,
        total_stalls=20,
        audience=AudienceType.VISITOR,
        day_of_week=2,
        hour=9,
    )
    res = provider.predict(ctx)

    assert res.predicted_usage == 6.0
    assert res.confidence == "medium"
    assert res.source == "heuristic"
    # ratio = 6.0 / 20 = 0.3 -> LOW
    assert res.crowd_level == "LOW"


def test_heuristic_provider_tier1_high(db_session):
    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    from app.models.category import Category

    c = Category(code="test_cat_2", label="Test Category 2")
    db_session.add(c)
    db_session.flush()

    f = seed_facility(db_session, "F2", c.id, total_stalls=20, audience=AudienceType.VISITOR)

    for i in range(8):
        usage_repo.upsert_hourly_record(
            facility_id=f.id,
            record_date=date(2026, 9, 1 + i),
            hour=9,
            day_of_week=2,
            usage_count=10,
            data_source=DataSource.SYNTHETIC,
        )

    provider = HeuristicUsageProvider(usage_repo, facility_repo)
    ctx = PredictionContext(
        facility_id=f.id,
        category_id=c.id,
        total_stalls=20,
        audience=AudienceType.VISITOR,
        day_of_week=2,
        hour=9,
    )
    res = provider.predict(ctx)

    assert res.predicted_usage == 10.0
    assert res.confidence == "high"


def test_heuristic_provider_tier2(db_session):
    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    from app.models.category import Category

    c = Category(code="test_cat_3", label="Test Category 3")
    db_session.add(c)
    db_session.flush()

    f1 = seed_facility(db_session, "F_Target", c.id, total_stalls=20, audience=AudienceType.VISITOR)
    f2 = seed_facility(db_session, "F_Peer", c.id, total_stalls=20, audience=AudienceType.VISITOR)

    # 0 rows for target f1. 3 rows for peer f2.
    for i in range(3):
        usage_repo.upsert_hourly_record(
            facility_id=f2.id,
            record_date=date(2026, 9, 1 + i),
            hour=9,
            day_of_week=2,
            usage_count=15,
            data_source=DataSource.SYNTHETIC,
        )

    provider = HeuristicUsageProvider(usage_repo, facility_repo)
    ctx = PredictionContext(
        facility_id=f1.id,
        category_id=c.id,
        total_stalls=20,
        audience=AudienceType.VISITOR,
        day_of_week=2,
        hour=9,
    )
    res = provider.predict(ctx)

    assert res.predicted_usage == 15.0
    assert res.confidence == "low"


def test_heuristic_provider_tier3(db_session):
    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    from app.models.category import Category

    c1 = Category(code="cat_target", label="Cat Target")
    c2 = Category(code="cat_other", label="Cat Other")
    db_session.add_all([c1, c2])
    db_session.flush()

    f1 = seed_facility(
        db_session, "F_Target", c1.id, total_stalls=20, audience=AudienceType.VISITOR
    )
    f2 = seed_facility(
        db_session, "F_OtherCat", c2.id, total_stalls=20, audience=AudienceType.VISITOR
    )

    # 0 rows for target facility and category. 1 row for a completely different category.
    usage_repo.upsert_hourly_record(
        facility_id=f2.id,
        record_date=date(2026, 9, 1),
        hour=9,
        day_of_week=2,
        usage_count=50,
        data_source=DataSource.SYNTHETIC,
    )

    provider = HeuristicUsageProvider(usage_repo, facility_repo)
    ctx = PredictionContext(
        facility_id=f1.id,
        category_id=c1.id,
        total_stalls=20,
        audience=AudienceType.VISITOR,
        day_of_week=2,
        hour=9,
    )
    res = provider.predict(ctx)

    assert res.predicted_usage == 50.0
    assert res.confidence == "low"


def test_heuristic_provider_tier4_and_zero_stalls_fallback(db_session):
    usage_repo = UsageRecordRepository(db_session)
    facility_repo = FacilityRepository(db_session)
    from app.models.category import Category

    c = Category(code="cat_fallback", label="Cat fallback")
    db_session.add(c)
    db_session.flush()

    f1 = seed_facility(db_session, "F_NoCap", c.id, total_stalls=0, audience=AudienceType.VISITOR)

    # No usage records anywhere
    provider = HeuristicUsageProvider(usage_repo, facility_repo)
    ctx = PredictionContext(
        facility_id=f1.id,
        category_id=c.id,
        total_stalls=0,
        audience=AudienceType.VISITOR,
        day_of_week=2,
        hour=9,
    )
    res = provider.predict(ctx)

    assert res.predicted_usage == 0.0
    assert res.confidence == "low"
    # fallback cap = 10, ratio = 0.0 -> LOW
    assert res.crowd_level == "LOW"
