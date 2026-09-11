"""Unit tests for the pure OSRM client functions.

No HTTP calls, no DB — pure fixture-based input/output testing.
"""

import pytest

from app.domain.routing.osrm_client import (
    OSRMNoRouteError,
    build_route_request_url,
    parse_osrm_route_response,
)

# ── build_route_request_url ─────────────────────────────────────────────────


class TestBuildRouteRequestUrl:
    def test_url_shape(self) -> None:
        url = build_route_request_url(
            "https://router.project-osrm.org",
            origin_lat=7.2545,
            origin_lon=80.5965,
            dest_lat=7.260,
            dest_lon=80.600,
        )
        assert url.startswith("https://router.project-osrm.org/route/v1/foot/")
        # OSRM expects lon,lat order
        assert "80.5965,7.2545" in url  # origin: lon,lat
        assert "80.6,7.26" in url  # dest: lon,lat
        assert "overview=full" in url
        assert "geometries=geojson" in url

    def test_coordinate_order_is_lon_lat(self) -> None:
        """OSRM requires lon,lat NOT lat,lon — verify explicitly."""
        url = build_route_request_url(
            "https://router.project-osrm.org",
            origin_lat=10.0,
            origin_lon=20.0,
            dest_lat=11.0,
            dest_lon=21.0,
        )
        # Should be /foot/20.0,10.0;21.0,11.0 (lon first)
        assert "/foot/20.0,10.0;21.0,11.0" in url


# ── parse_osrm_route_response ───────────────────────────────────────────────

_OSRM_SUCCESS_BODY = {
    "code": "Ok",
    "routes": [
        {
            "distance": 450.3,
            "duration": 375,
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [80.5965, 7.2545],  # [lon, lat]
                    [80.5970, 7.2550],
                    [80.5975, 7.2555],
                ],
            },
        }
    ],
}

_OSRM_EMPTY_ROUTES_BODY = {
    "code": "NoRoute",
    "routes": [],
}

_OSRM_MISSING_ROUTES_BODY = {
    "code": "NoRoute",
}


class TestParseOsrmRouteResponse:
    def test_success_returns_route_result(self) -> None:
        result = parse_osrm_route_response(_OSRM_SUCCESS_BODY)
        assert result.source == "network"
        assert result.distance_m == pytest.approx(450.3)
        assert result.estimated_time_s == 375

    def test_path_is_lat_lon_pairs(self) -> None:
        """Coordinates from GeoJSON are [lon, lat]; the parser must swap them."""
        result = parse_osrm_route_response(_OSRM_SUCCESS_BODY)
        # First coordinate in GeoJSON was [80.5965, 7.2545] (lon, lat)
        # After swap it should be (7.2545, 80.5965) (lat, lon)
        assert result.path[0] == pytest.approx((7.2545, 80.5965))
        assert result.path[1] == pytest.approx((7.2550, 80.5970))
        assert result.path[2] == pytest.approx((7.2555, 80.5975))

    def test_path_length_matches_coordinates(self) -> None:
        result = parse_osrm_route_response(_OSRM_SUCCESS_BODY)
        assert len(result.path) == 3

    def test_empty_routes_raises_no_route_error(self) -> None:
        with pytest.raises(OSRMNoRouteError):
            parse_osrm_route_response(_OSRM_EMPTY_ROUTES_BODY)

    def test_missing_routes_key_raises_no_route_error(self) -> None:
        with pytest.raises(OSRMNoRouteError):
            parse_osrm_route_response(_OSRM_MISSING_ROUTES_BODY)
