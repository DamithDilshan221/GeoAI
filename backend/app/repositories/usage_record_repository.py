"""Usage record repository — owner of all queries against ``usage_records``."""

from datetime import date

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.domain.entities import UsageRecord as UsageRecordEntity
from app.models.enums import DataSource
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
