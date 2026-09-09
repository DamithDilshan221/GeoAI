"""Usage record repository — owner of all queries against ``usage_records``."""

from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.domain.entities import UsageRecord as UsageRecordEntity
from app.models.enums import DataSource
from app.models.facility import Facility as FacilityORM
from app.models.usage_record import UsageRecord as UsageRecordORM


class UsageRecordRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_hourly_record(
        self,
        *,
        facility_id: int,
        record_date: date,
        hour: int,
        day_of_week: int,
        usage_count: int,
        data_source: DataSource,
    ) -> UsageRecordEntity:
        """Upsert a usage record for a specific facility, date, and hour.

        Uses PostgreSQL's native INSERT ... ON CONFLICT DO UPDATE.
        Note selection_count is deliberately NOT in the update set — an upsert
        here must never reset a real selection_count that Phase 13 may have
        already written for this bucket.
        """
        stmt = insert(UsageRecordORM).values(
            facility_id=facility_id,
            date=record_date,
            hour=hour,
            day_of_week=day_of_week,
            usage_count=usage_count,
            data_source=data_source,
            # selection_count defaults to 0 on insert, ignored on update
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["facility_id", "date", "hour"],
            set_={
                "usage_count": usage_count,
                "day_of_week": day_of_week,
                "data_source": data_source,
            },
        ).returning(UsageRecordORM)

        orm = self._session.execute(stmt).scalar_one()
        self._session.flush()

        return UsageRecordEntity(
            id=orm.id,
            facility_id=orm.facility_id,
            date=orm.date,
            hour=orm.hour,
            day_of_week=orm.day_of_week,
            usage_count=orm.usage_count,
            selection_count=orm.selection_count,
            data_source=orm.data_source,
        )

    def count_for_facility(self, facility_id: int) -> int:
        """Return the total number of usage records for a given facility."""
        return (
            self._session.query(UsageRecordORM)
            .filter(UsageRecordORM.facility_id == facility_id)
            .count()
        )

    def get_facility_bucket_average(
        self, *, facility_id: int, day_of_week: int, hour: int,
    ) -> tuple[float, int] | None:
        """Returns (mean_usage_count, sample_count), or None if zero rows
        match. SELECT AVG(usage_count), COUNT(*) FROM usage_records WHERE
        facility_id=:fid AND day_of_week=:dow AND hour=:h."""
        row = self._session.execute(
            sa.select(sa.func.avg(UsageRecordORM.usage_count), sa.func.count())
            .where(
                UsageRecordORM.facility_id == facility_id,
                UsageRecordORM.day_of_week == day_of_week,
                UsageRecordORM.hour == hour,
            )
        ).one_or_none()
        if not row or row[1] == 0:
            return None
        return (float(row[0]), int(row[1]))

    def get_category_bucket_average(
        self, *, category_id: int, day_of_week: int, hour: int,
    ) -> tuple[float, int] | None:
        """Same shape, joined against facilities to filter by category_id
        instead of a single facility_id."""
        row = self._session.execute(
            sa.select(sa.func.avg(UsageRecordORM.usage_count), sa.func.count())
            .select_from(UsageRecordORM)
            .join(FacilityORM, UsageRecordORM.facility_id == FacilityORM.id)
            .where(
                FacilityORM.category_id == category_id,
                UsageRecordORM.day_of_week == day_of_week,
                UsageRecordORM.hour == hour,
            )
        ).one_or_none()
        if not row or row[1] == 0:
            return None
        return (float(row[0]), int(row[1]))

    def get_global_bucket_average(
        self, *, day_of_week: int, hour: int,
    ) -> tuple[float, int] | None:
        """Same shape, no facility/category filter at all."""
        row = self._session.execute(
            sa.select(sa.func.avg(UsageRecordORM.usage_count), sa.func.count())
            .where(
                UsageRecordORM.day_of_week == day_of_week,
                UsageRecordORM.hour == hour,
            )
        ).one_or_none()
        if not row or row[1] == 0:
            return None
        return (float(row[0]), int(row[1]))
