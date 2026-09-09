from datetime import date

from app.domain.usage_data.synthetic_generator import (
    date_range_for_history,
    generate_synthetic_usage_count,
)


def test_determinism():
    """Same input always produces identical output."""
    res1 = generate_synthetic_usage_count(
        facility_id=1, capacity=50, target_date=date(2026, 9, 10), hour=14
    )
    res2 = generate_synthetic_usage_count(
        facility_id=1, capacity=50, target_date=date(2026, 9, 10), hour=14
    )
    assert res1 == res2


def test_different_facilities_differ():
    """Two different facility_ids with same inputs produce different results."""
    res1 = generate_synthetic_usage_count(
        facility_id=1, capacity=50, target_date=date(2026, 9, 10), hour=14
    )
    res2 = generate_synthetic_usage_count(
        facility_id=2, capacity=50, target_date=date(2026, 9, 10), hour=14
    )
    assert res1 != res2


def test_hourly_curve_shape():
    """Averaged over many dates, peak hour (9) is higher than off-peak (3)."""
    h9_sum = 0
    h3_sum = 0
    dates = date_range_for_history(30, today=date(2026, 9, 10))
    for d in dates:
        h9_sum += generate_synthetic_usage_count(facility_id=1, capacity=50, target_date=d, hour=9)
        h3_sum += generate_synthetic_usage_count(facility_id=1, capacity=50, target_date=d, hour=3)

    assert h9_sum > h3_sum


def test_weekend_multiplier():
    """A Saturday (day 5) produces lower mean than a Wednesday (day 2)."""
    # Test across multiple facilities to avoid RNG flukes
    sat_sum = 0
    wed_sum = 0
    sat_date = date(2026, 9, 5)  # Sept 5 2026 is a Saturday
    wed_date = date(2026, 9, 9)  # Sept 9 2026 is a Wednesday

    for f_id in range(1, 20):
        sat_sum += generate_synthetic_usage_count(
            facility_id=f_id, capacity=50, target_date=sat_date, hour=12
        )
        wed_sum += generate_synthetic_usage_count(
            facility_id=f_id, capacity=50, target_date=wed_date, hour=12
        )

    assert sat_sum < wed_sum


def test_non_negative_and_capacity_fallback():
    """Handles capacity=None and capacity=0 gracefully (always >= 0)."""
    res_none = generate_synthetic_usage_count(
        facility_id=1, capacity=None, target_date=date(2026, 9, 10), hour=12
    )
    assert res_none >= 0

    res_zero = generate_synthetic_usage_count(
        facility_id=1, capacity=0, target_date=date(2026, 9, 10), hour=12
    )
    assert res_zero == 0


def test_date_range_for_history():
    """Returns exact days, ending yesterday, oldest first."""
    today = date(2026, 9, 10)
    dates = date_range_for_history(7, today=today)

    assert len(dates) == 7
    assert dates[0] == date(2026, 9, 3)
    assert dates[-1] == date(2026, 9, 9)
    # Today is explicitly not included
    assert today not in dates
