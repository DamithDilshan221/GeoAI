"""Unit tests for PedestrianRoutingService — httpx mocked, no live network calls."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.domain.entities import Facility
from app.domain.gis.distance_estimation import estimate_distance_m
from app.domain.routing.pedestrian_routing_service import PedestrianRoutingService
from app.models.enums import AudienceType, DataSource, FacilityStatus

# ── Helpers ─────────────────────────────────────────────────────────────────

_NOW = datetime(2026, 1, 1, 12, 0, 0)
_ORIGIN_LAT = 7.2545
_ORIGIN_LON = 80.5965
_DEST_LAT = 7.260
_DEST_LON = 80.600


def _make_facility(fid: int = 1) -> Facility:
    return Facility(
        id=fid,
        name="Test WC",
        category_id=1,
        latitude=_DEST_LAT,
        longitude=_DEST_LON,
        status=FacilityStatus.OPEN,
        status_updated_at=_NOW,
        rating=None,
        audience=AudienceType.VISITOR,
        location_name=None,
        fixtures={},
        total_stalls=2,
        data_source=DataSource.SYNTHETIC,
        is_active=True,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _make_service(facility: Facility | None = None) -> tuple[PedestrianRoutingService, MagicMock]:
    facility_repo = MagicMock()
    facility_repo.get_by_id.return_value = facility
    svc = PedestrianRoutingService(
        facility_repo=facility_repo,
        osrm_base_url="https://router.project-osrm.org",
        walking_speed_mps=1.2,
    )
    return svc, facility_repo


_OSRM_SUCCESS_JSON = {
    "code": "Ok",
    "routes": [
        {
            "distance": 523.0,
            "duration": 436,
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [_ORIGIN_LON, _ORIGIN_LAT],
                    [_DEST_LON, _DEST_LAT],
                ],
            },
        }
    ],
}


# ── Tests ────────────────────────────────────────────────────────────────────


class TestGetRouteSuccess:
    def test_returns_network_route(self) -> None:
        svc, _ = _make_service(_make_facility())
        mock_response = MagicMock()
        mock_response.json.return_value = _OSRM_SUCCESS_JSON
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.get", return_value=mock_response):
            result = svc.get_route(
                origin_lat=_ORIGIN_LAT,
                origin_lon=_ORIGIN_LON,
                facility_id=1,
            )

        assert result is not None
        assert result.source == "network"
        assert result.distance_m == pytest.approx(523.0)
        assert result.estimated_time_s == 436

    def test_distance_comes_from_osrm_not_haversine(self) -> None:
        svc, _ = _make_service(_make_facility())
        mock_response = MagicMock()
        mock_response.json.return_value = _OSRM_SUCCESS_JSON
        mock_response.raise_for_status = MagicMock()

        # Distance from OSRM fixture is 523.0 m; Haversine would give a different value
        haversine_dist = estimate_distance_m(
            origin_lat=_ORIGIN_LAT,
            origin_lon=_ORIGIN_LON,
            dest_lat=_DEST_LAT,
            dest_lon=_DEST_LON,
        )
        with patch("httpx.get", return_value=mock_response):
            result = svc.get_route(origin_lat=_ORIGIN_LAT, origin_lon=_ORIGIN_LON, facility_id=1)

        assert result is not None
        # Network result distance differs from Haversine straight-line
        assert abs(result.distance_m - haversine_dist) > 1.0  # not the same value


class TestGetRouteFallback:
    def test_connection_error_falls_back_to_straight_line(self) -> None:
        svc, _ = _make_service(_make_facility())

        with patch("httpx.get", side_effect=httpx.ConnectError("unreachable")):
            result = svc.get_route(
                origin_lat=_ORIGIN_LAT,
                origin_lon=_ORIGIN_LON,
                facility_id=1,
            )

        assert result is not None
        assert result.source == "straight_line_estimate"

    def test_fallback_distance_matches_estimate_distance_m(self) -> None:
        """Fallback distance must equal estimate_distance_m's own output, not a magic number."""
        svc, _ = _make_service(_make_facility())
        expected_dist = estimate_distance_m(
            origin_lat=_ORIGIN_LAT,
            origin_lon=_ORIGIN_LON,
            dest_lat=_DEST_LAT,
            dest_lon=_DEST_LON,
        )

        with patch("httpx.get", side_effect=httpx.ConnectError("unreachable")):
            result = svc.get_route(
                origin_lat=_ORIGIN_LAT,
                origin_lon=_ORIGIN_LON,
                facility_id=1,
            )

        assert result is not None
        assert result.distance_m == pytest.approx(expected_dist)

    def test_empty_routes_array_falls_back(self) -> None:
        svc, _ = _make_service(_make_facility())
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": "NoRoute", "routes": []}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.get", return_value=mock_response):
            result = svc.get_route(
                origin_lat=_ORIGIN_LAT,
                origin_lon=_ORIGIN_LON,
                facility_id=1,
            )

        assert result is not None
        assert result.source == "straight_line_estimate"

    def test_fallback_path_has_two_points(self) -> None:
        svc, _ = _make_service(_make_facility())

        with patch("httpx.get", side_effect=httpx.ConnectError("unreachable")):
            result = svc.get_route(
                origin_lat=_ORIGIN_LAT,
                origin_lon=_ORIGIN_LON,
                facility_id=1,
            )

        assert result is not None
        assert len(result.path) == 2
        assert result.path[0] == (_ORIGIN_LAT, _ORIGIN_LON)
        assert result.path[1] == (_DEST_LAT, _DEST_LON)


class TestGetRouteFacilityNotFound:
    def test_returns_none_without_calling_httpx(self) -> None:
        svc, facility_repo = _make_service(facility=None)

        with patch("httpx.get") as mock_get:
            result = svc.get_route(
                origin_lat=_ORIGIN_LAT,
                origin_lon=_ORIGIN_LON,
                facility_id=999,
            )

        assert result is None
        mock_get.assert_not_called()


class TestAccessibleOnlyIsNoop:
    def test_accessible_true_produces_same_url_as_false(self) -> None:
        """accessible_only is inert — both must produce the identical request URL."""
        svc, _ = _make_service(_make_facility())
        mock_response = MagicMock()
        mock_response.json.return_value = _OSRM_SUCCESS_JSON
        mock_response.raise_for_status = MagicMock()

        captured_urls: list[str] = []

        def capture_url(url: str, **kwargs: object) -> MagicMock:
            captured_urls.append(url)
            return mock_response

        with patch("httpx.get", side_effect=capture_url):
            svc.get_route(
                origin_lat=_ORIGIN_LAT, origin_lon=_ORIGIN_LON, facility_id=1, accessible_only=False
            )
            svc.get_route(
                origin_lat=_ORIGIN_LAT, origin_lon=_ORIGIN_LON, facility_id=1, accessible_only=True
            )

        assert len(captured_urls) == 2
        assert captured_urls[0] == captured_urls[1], (
            "accessible_only must not affect the OSRM request URL"
        )
