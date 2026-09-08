"""Haversine formula for estimating straight-line distances.

This provides a fallback distance and path for pedestrian routing when the
pgRouting network is disconnected or no path can be found.
"""

import math

# Mean radius of the Earth in meters
EARTH_RADIUS_M = 6371000.0


def estimate_distance_m(*, origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> float:
    """Calculate the great-circle distance between two points in meters using Haversine formula.

    This provides a fallback straight-line distance if network routing fails.
    """
    phi1 = math.radians(origin_lat)
    phi2 = math.radians(dest_lat)
    delta_phi = math.radians(dest_lat - origin_lat)
    delta_lambda = math.radians(dest_lon - origin_lon)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_M * c
