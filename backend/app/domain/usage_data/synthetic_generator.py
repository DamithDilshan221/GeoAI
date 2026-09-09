"""Synthetic usage history generator (spec §14.2, Phase 9)."""

import random
from datetime import date, timedelta

# Hourly traffic shape: low overnight, peaks around lunch/class-changes
HOURLY_CURVE = [
    0.05,
    0.05,
    0.05,
    0.05,
    0.05,
    0.10,  # 0-5: overnight
    0.20,
    0.50,
    0.90,
    1.00,
    0.70,
    0.80,  # 6-11: morning ramp + peak
    1.00,
    0.90,
    0.60,
    0.70,
    0.90,
    0.80,  # 12-17: lunch peak + afternoon
    0.50,
    0.40,
    0.30,
    0.20,
    0.10,
    0.05,  # 18-23: evening taper
]

WEEKEND_MULTIPLIER = 0.15


def deterministic_unit_random(key: str) -> float:
    """Return a deterministic float in [0, 1) based on the string key."""
    return random.Random(key).random()


def generate_synthetic_usage_count(
    *, facility_id: int, capacity: int | None, target_date: date, hour: int
) -> int:
    """Deterministically generate a synthetic usage count bucket.

    day_of_week convention: Python's date.weekday() — Monday=0, Sunday=6.
    Phase 10's heuristic and Phase 15's ML features both read this column
    assuming this exact convention — do not change it without updating both.
    """
    day_of_week = target_date.weekday()

    base_rate = (capacity if capacity is not None else 10) * 0.8
    facility_multiplier = 0.7 + 0.6 * deterministic_unit_random(f"facility:{facility_id}")
    noise = 0.8 + 0.4 * deterministic_unit_random(f"{facility_id}:{target_date.isoformat()}:{hour}")

    usage_count = round(
        base_rate
        * facility_multiplier
        * HOURLY_CURVE[hour]
        * (WEEKEND_MULTIPLIER if day_of_week >= 5 else 1.0)
        * noise
    )

    return max(0, usage_count)


def date_range_for_history(days: int, *, today: date | None = None) -> list[date]:
    """Return exactly `days` dates ending yesterday, oldest first."""
    if today is None:
        today = date.today()

    end_date = today - timedelta(days=1)
    return [end_date - timedelta(days=days - i - 1) for i in range(days)]
