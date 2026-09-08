import pytest

from app.domain.gis.distance_estimation import estimate_distance_m


def test_estimate_distance_m_same_point():
    distance = estimate_distance_m(origin_lat=0.0, origin_lon=0.0, dest_lat=0.0, dest_lon=0.0)
    assert distance == 0.0


def test_estimate_distance_m_known_distance():
    # Roughly one degree of latitude is ~111,320 meters
    distance = estimate_distance_m(origin_lat=0.0, origin_lon=0.0, dest_lat=1.0, dest_lon=0.0)
    assert pytest.approx(distance, rel=1e-2) == 111320.0
