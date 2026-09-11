"""Synthetic usage history generator (spec §14.2, Phase 9)."""

import random
from datetime import date, timedelta
from app.models.enums import AudienceType

# Hourly traffic shape: low overnight, peaks around lunch/class-changes
VISITOR_HOURLY_CURVE = [
    0.05, 0.05, 0.05, 0.05, 0.05, 0.10,
    0.20, 0.50, 0.90, 1.00, 0.70, 0.80,
    1.00, 0.90, 0.60, 0.70, 0.90, 0.80,
    0.50, 0.40, 0.30, 0.20, 0.10, 0.05,
]
STAFF_HOURLY_CURVE = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.3, 0.7, 0.9, 1.0, 0.7,
    0.8, 0.9, 0.7, 0.6, 0.5, 0.3,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
]

AUDIENCE_MULTIPLIER = {"VISITOR": 1.0, "STAFF": 0.4}
VISITOR_WEEKEND_MULTIPLIER = 0.15
STAFF_WEEKEND_MULTIPLIER = 0.05

def deterministic_unit_random(key: str) -> float:
    """Return a deterministic float in [0, 1) based on the string key."""
    return random.Random(key).random()


def generate_synthetic_usage_count(
    *, facility_id: int, total_stalls: int, audience: AudienceType, target_date: date, hour: int
) -> int:
    """Deterministically generate a synthetic usage count bucket.

    day_of_week convention: Python's date.weekday() — Monday=0, Sunday=6.
    Phase 10's heuristic and Phase 15's ML features both read this column
    assuming this exact convention — do not change it without updating both.
    """
    day_of_week = target_date.weekday()

    effective_stalls = total_stalls if total_stalls > 0 else 1
    base_rate = effective_stalls * 0.8
    audience_multiplier = AUDIENCE_MULTIPLIER[audience.value]
    curve = STAFF_HOURLY_CURVE if audience == AudienceType.STAFF else VISITOR_HOURLY_CURVE
    weekend_multiplier = (STAFF_WEEKEND_MULTIPLIER if audience == AudienceType.STAFF 
                          else VISITOR_WEEKEND_MULTIPLIER) if day_of_week >= 5 else 1.0

    facility_multiplier = 0.7 + 0.6 * deterministic_unit_random(f"facility:{facility_id}")
    noise = 0.8 + 0.4 * deterministic_unit_random(f"{facility_id}:{target_date.isoformat()}:{hour}")

    usage_count = round(
        base_rate * audience_multiplier * facility_multiplier
        * curve[hour] * weekend_multiplier * noise
    )

    return max(0, usage_count)


def date_range_for_history(days: int, *, today: date | None = None) -> list[date]:
    """Return exactly `days` dates ending yesterday, oldest first."""
    if today is None:
        today = date.today()

    end_date = today - timedelta(days=1)
    return [end_date - timedelta(days=days - i - 1) for i in range(days)]
