from datetime import date

import pytest
from sqlalchemy import text

from app.domain.entities import UsageRecord as UsageRecordEntity
from app.models.enums import DataSource
from app.repositories.usage_record_repository import UsageRecordRepository


@pytest.fixture
def repo(db_session):
    return UsageRecordRepository(db_session)


@pytest.fixture
def test_facility_id(db_session):
    """Seed a minimal facility for testing foreign key constraints."""
    # Assuming test database is already seeded via another mechanism,
    # or just manually seed one here. Let's seed one directly via SQL.
    # Phase 2 migrations should have created the categories and facilities tables.
    db_session.execute(
        text(
            "INSERT INTO categories (id, code, label) "
            "VALUES (999, 'test_cat', 'Test') ON CONFLICT DO NOTHING"
        )
    )
    db_session.execute(
        text(
            "INSERT INTO facilities "
            "(id, name, location_name, category_id, latitude, longitude, "
            "geom, status, data_source) "
            "VALUES (9999, 'Test Fac', 'Building Test', 999, 0.0, 0.0, "
            "ST_SetSRID(ST_MakePoint(0, 0), 4326), 'OPEN', 'PUBLIC') "
            "ON CONFLICT DO NOTHING"
        )
    )
    db_session.commit()
    return 9999


def test_upsert_hourly_record_inserts_new(repo, test_facility_id):
    """First upsert for a given bucket inserts a new row."""
    record = repo.upsert_hourly_record(
        facility_id=test_facility_id,
        record_date=date(2026, 9, 1),
        hour=10,
        day_of_week=1,  # Tuesday
        usage_count=42,
        data_source=DataSource.SYNTHETIC,
    )

    assert isinstance(record, UsageRecordEntity)
    assert record.usage_count == 42
    assert record.selection_count == 0
    assert repo.count_for_facility(test_facility_id) >= 1


def test_upsert_hourly_record_updates_existing(repo, test_facility_id):
    """Second upsert for SAME bucket UPDATES existing row."""
    # Insert first
    repo.upsert_hourly_record(
        facility_id=test_facility_id,
        record_date=date(2026, 9, 2),
        hour=11,
        day_of_week=2,
        usage_count=10,
        data_source=DataSource.SYNTHETIC,
    )
    count_before = repo.count_for_facility(test_facility_id)

    # Upsert again
    record_updated = repo.upsert_hourly_record(
        facility_id=test_facility_id,
        record_date=date(2026, 9, 2),
        hour=11,
        day_of_week=2,
        usage_count=99,
        data_source=DataSource.SYNTHETIC,
    )

    count_after = repo.count_for_facility(test_facility_id)
    assert count_before == count_after  # No new row
    assert record_updated.usage_count == 99


def test_day_of_week_matches(repo, test_facility_id):
    """The stored day_of_week matches what is passed."""
    record = repo.upsert_hourly_record(
        facility_id=test_facility_id,
        record_date=date(2026, 9, 1),  # Tuesday = 1
        hour=12,
        day_of_week=date(2026, 9, 1).weekday(),
        usage_count=10,
        data_source=DataSource.SYNTHETIC,
    )
    assert record.day_of_week == 1


def test_upsert_does_not_reset_selection_count(repo, db_session, test_facility_id):
    """Upsert ignores selection_count and leaves existing values intact."""
    # Seed a row with selection_count=5
    db_session.execute(
        text(
            "INSERT INTO usage_records "
            "(facility_id, date, hour, day_of_week, usage_count, selection_count, data_source) "
            "VALUES (:fid, '2026-09-03', 14, 3, 10, 5, 'SYNTHETIC')"
        ),
        {"fid": test_facility_id},
    )
    db_session.flush()

    # Upsert should update usage_count but keep selection_count=5
    record = repo.upsert_hourly_record(
        facility_id=test_facility_id,
        record_date=date(2026, 9, 3),
        hour=14,
        day_of_week=3,
        usage_count=100,
        data_source=DataSource.SYNTHETIC,
    )

    assert record.usage_count == 100
    assert record.selection_count == 5
