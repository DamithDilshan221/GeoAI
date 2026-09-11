from datetime import date

from app.domain.usage_data.synthetic_generator import (
    date_range_for_history,
    generate_synthetic_usage_count,
)
from app.models.enums import AudienceType


def test_determinism():
    """Same input always produces identical output."""
    res1 = generate_synthetic_usage_count(
        facility_id=1,
        total_stalls=10,
        audience=AudienceType.VISITOR,
        target_date=date(2026, 9, 10),
        hour=14,
    )
    res2 = generate_synthetic_usage_count(
        facility_id=1,
        total_stalls=10,
        audience=AudienceType.VISITOR,
        target_date=date(2026, 9, 10),
        hour=14,
    )
    assert res1 == res2


def test_different_facilities_differ():
    """Two different facility_ids with same inputs produce different results."""
    res1 = generate_synthetic_usage_count(
        facility_id=1,
        total_stalls=10,
        audience=AudienceType.VISITOR,
        target_date=date(2026, 9, 10),
        hour=14,
    )
    res2 = generate_synthetic_usage_count(
        facility_id=2,
        total_stalls=10,
        audience=AudienceType.VISITOR,
        target_date=date(2026, 9, 10),
        hour=14,
    )
    assert res1 != res2


def test_hourly_curve_shape():
    """Averaged over many dates, peak hour (9) is higher than off-peak (3) for Visitor."""
    h9_sum = 0
    h3_sum = 0
    dates = date_range_for_history(30, today=date(2026, 9, 10))
    for d in dates:
        h9_sum += generate_synthetic_usage_count(
            facility_id=1, total_stalls=10, audience=AudienceType.VISITOR, target_date=d, hour=9
        )
        h3_sum += generate_synthetic_usage_count(
            facility_id=1, total_stalls=10, audience=AudienceType.VISITOR, target_date=d, hour=3
        )

    assert h9_sum > h3_sum


def test_staff_vs_visitor_mean_usage():
    """Averaged over many simulated dates at the same hour, STAFF usage is lower than VISITOR."""
    staff_sum = 0
    visitor_sum = 0
    dates = date_range_for_history(30, today=date(2026, 9, 10))
    for d in dates:
        staff_sum += generate_synthetic_usage_count(
            facility_id=1, total_stalls=10, audience=AudienceType.STAFF, target_date=d, hour=10
        )
        visitor_sum += generate_synthetic_usage_count(
            facility_id=1, total_stalls=10, audience=AudienceType.VISITOR, target_date=d, hour=10
        )

    assert staff_sum < visitor_sum
    assert staff_sum > 0  # Ensure it's not always 0 at hour 10


def test_staff_off_hours_zero():
    """A STAFF facility's usage_count is exactly 0 at hour=2 and hour=22 across every date."""
    dates = date_range_for_history(30, today=date(2026, 9, 10))
    for d in dates:
        h2_usage = generate_synthetic_usage_count(
            facility_id=1, total_stalls=10, audience=AudienceType.STAFF, target_date=d, hour=2
        )
        h22_usage = generate_synthetic_usage_count(
            facility_id=1, total_stalls=10, audience=AudienceType.STAFF, target_date=d, hour=22
        )
        assert h2_usage == 0
        assert h22_usage == 0


def test_weekend_multiplier_differentiation():
    """STAFF Saturday usage drops by a larger relative margin from weekday than VISITOR does."""
    sat_date = date(2026, 9, 5)  # Saturday
    wed_date = date(2026, 9, 9)  # Wednesday

    staff_sat_sum = 0
    staff_wed_sum = 0
    visitor_sat_sum = 0
    visitor_wed_sum = 0

    # Sum across multiple facilities to average out the facility/noise RNG
    for f_id in range(1, 20):
        staff_sat_sum += generate_synthetic_usage_count(
            facility_id=f_id,
            total_stalls=10,
            audience=AudienceType.STAFF,
            target_date=sat_date,
            hour=12,
        )
        staff_wed_sum += generate_synthetic_usage_count(
            facility_id=f_id,
            total_stalls=10,
            audience=AudienceType.STAFF,
            target_date=wed_date,
            hour=12,
        )
        visitor_sat_sum += generate_synthetic_usage_count(
            facility_id=f_id,
            total_stalls=10,
            audience=AudienceType.VISITOR,
            target_date=sat_date,
            hour=12,
        )
        visitor_wed_sum += generate_synthetic_usage_count(
            facility_id=f_id,
            total_stalls=10,
            audience=AudienceType.VISITOR,
            target_date=wed_date,
            hour=12,
        )

    assert staff_sat_sum < staff_wed_sum
    assert visitor_sat_sum < visitor_wed_sum

    staff_ratio = staff_sat_sum / staff_wed_sum
    visitor_ratio = visitor_sat_sum / visitor_wed_sum

    # Staff drops harder on weekends than visitor
    assert staff_ratio < visitor_ratio


def test_empty_fixtures_fallback():
    """total_stalls=0 produces a non-negative, small-but-nonzero result (floor of 1, not 10)."""
    # Sum over multiple dates to ensure it triggers at least some usage
    dates = date_range_for_history(10, today=date(2026, 9, 10))
    zero_stalls_sum = 0
    six_stalls_sum = 0

    for d in dates:
        zero_stalls_sum += generate_synthetic_usage_count(
            facility_id=1, total_stalls=0, audience=AudienceType.VISITOR, target_date=d, hour=12
        )
        six_stalls_sum += generate_synthetic_usage_count(
            facility_id=1, total_stalls=6, audience=AudienceType.VISITOR, target_date=d, hour=12
        )

    assert zero_stalls_sum > 0
    # Proves it falls back to 1, not 10 (which would be larger than 6)
    assert zero_stalls_sum < six_stalls_sum


def test_date_range_for_history():
    """Returns exact days, ending yesterday, oldest first."""
    today = date(2026, 9, 10)
    dates = date_range_for_history(7, today=today)

    assert len(dates) == 7
    assert dates[0] == date(2026, 9, 3)
    assert dates[-1] == date(2026, 9, 9)
    # Today is explicitly not included
    assert today not in dates
