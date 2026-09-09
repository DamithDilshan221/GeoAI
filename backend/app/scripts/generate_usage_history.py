"""Generate deterministic synthetic historical usage data.

This script populates the usage_records table with repeatable,
structured hourly usage buckets for all active facilities.
"""

import argparse
import sys

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import engine
from app.domain.usage_data.synthetic_generator import (
    date_range_for_history,
    generate_synthetic_usage_count,
)
from app.models.enums import DataSource
from app.repositories.facility_repository import FacilityRepository
from app.repositories.usage_record_repository import UsageRecordRepository


def main() -> None:
    settings = get_settings()

    parser = argparse.ArgumentParser(description="Generate synthetic usage history.")
    parser.add_argument(
        "--days",
        type=int,
        default=settings.USAGE_HISTORY_DAYS,
        help=f"Number of past days to generate (default: {settings.USAGE_HISTORY_DAYS})",
    )
    args = parser.parse_args()

    dates = date_range_for_history(args.days)
    if not dates:
        print("No days to generate. Exiting.")
        return

    print(f"Targeting database: {settings.DATABASE_URL}")
    print(f"Generating usage history for {args.days} days ({dates[0]} to {dates[-1]})...")

    with Session(engine) as session:
        facility_repo = FacilityRepository(session)
        usage_repo = UsageRecordRepository(session)

        active_ids = facility_repo.list_all_active_ids()
        facility_count = len(active_ids)
        if not facility_count:
            print("No active facilities found. Exiting.")
            return

        print(f"Found {facility_count} active facilities.")

        total_upserted = 0
        hour_9_total = 0
        hour_3_total = 0

        # We loop over facilities, caching their capacity
        for f_id in active_ids:
            facility = facility_repo.get_by_id(f_id)
            if not facility:
                continue

            capacity = facility.capacity

            for d in dates:
                day_of_week = d.weekday()
                for hour in range(24):
                    usage_count = generate_synthetic_usage_count(
                        facility_id=f_id, capacity=capacity, target_date=d, hour=hour
                    )

                    usage_repo.upsert_hourly_record(
                        facility_id=f_id,
                        record_date=d,
                        hour=hour,
                        day_of_week=day_of_week,
                        usage_count=usage_count,
                        data_source=DataSource.SYNTHETIC,
                    )
                    total_upserted += 1

                    if hour == 9:
                        hour_9_total += usage_count
                    elif hour == 3:
                        hour_3_total += usage_count

        # Commit once at the end
        session.commit()

        hour_9_avg = (
            hour_9_total / (facility_count * args.days) if facility_count * args.days > 0 else 0
        )
        hour_3_avg = (
            hour_3_total / (facility_count * args.days) if facility_count * args.days > 0 else 0
        )

        print("\n--- Summary ---")
        print(f"Total rows upserted: {total_upserted}")
        print(f"Sanity Check: Avg usage at 09:00 (peak): {hour_9_avg:.1f}")
        print(f"Sanity Check: Avg usage at 03:00 (off-peak): {hour_3_avg:.1f}")


if __name__ == "__main__":
    sys.exit(main())
