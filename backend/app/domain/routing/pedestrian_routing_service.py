"""OSRM-backed pedestrian routing service.

Moved from ``domain/gis/`` to ``domain/routing/`` per §11's structural directive —
GIS is for PostGIS spatial queries; routing is its own concern.

Constructor changes from the dead ``(routing_repo, facility_repo)`` shape to
``(facility_repo, osrm_base_url, walking_speed_mps)`` — there is no repository
dependency left because there is no database query left in this service's job.

The public method signature ``get_route(*, origin_lat, origin_lon, facility_id,
accessible_only=False)`` is unchanged so existing callers need no update.
``accessible_only`` is accepted but is currently inert under OSRM's public foot
profile (no wheelchair-avoidance concept exists without a custom profile).
This is documented here rather than silently dropped.
"""

import logging

import httpx

from app.domain.entities import RouteResult
from app.domain.gis.coordinate_validation import validate_coordinates
from app.domain.gis.distance_estimation import estimate_distance_m
from app.domain.gis.exceptions import CoordinateValidationError  # noqa: F401 (re-exported)
from app.domain.routing.osrm_client import (
    OSRMNoRouteError,
    build_route_request_url,
    parse_osrm_route_response,
)
from app.repositories.facility_repository import FacilityRepository

logger = logging.getLogger(__name__)


class PedestrianRoutingService:
    """Walking route computation via the OSRM public ``foot`` profile.

    Falls back to a straight-line Haversine estimate on any OSRM error
    (connection failure, timeout, empty routes array, malformed response)
    per §14.4/§22.1.
    """

    def __init__(
        self,
        facility_repo: FacilityRepository,
        osrm_base_url: str,
        walking_speed_mps: float,
    ) -> None:
        self._facility_repo = facility_repo
        self._osrm_base_url = osrm_base_url
        self._walking_speed_mps = walking_speed_mps

    def get_route(
        self,
        *,
        origin_lat: float,
        origin_lon: float,
        facility_id: int,
        accessible_only: bool = False,  # noqa: ARG002 — accepted, currently inert under OSRM
    ) -> RouteResult | None:
        """Return a ``RouteResult`` for walking from the origin to the facility.

        Returns ``None`` if the facility does not exist in the database.
        Never raises on OSRM errors — falls back to a straight-line estimate instead.

        Note: ``accessible_only`` is accepted for API compatibility with callers
        that set it but is currently a no-op.  The public OSRM ``foot`` profile
        has no wheelchair-avoidance concept without a custom profile (§14.3).
        """
        validate_coordinates(lat=origin_lat, lon=origin_lon)

        facility = self._facility_repo.get_by_id(facility_id)
        if facility is None:
            return None

        try:
            url = build_route_request_url(
                self._osrm_base_url,
                origin_lat,
                origin_lon,
                facility.latitude,
                facility.longitude,
            )
            response = httpx.get(url, timeout=5.0)
            response.raise_for_status()
            return parse_osrm_route_response(response.json())
        except (httpx.HTTPError, OSRMNoRouteError, ValueError, KeyError) as exc:
            logger.warning(
                "OSRM routing failed for facility %d (%s); using straight-line fallback",
                facility_id,
                exc,
            )
            distance_m = estimate_distance_m(
                origin_lat=origin_lat,
                origin_lon=origin_lon,
                dest_lat=facility.latitude,
                dest_lon=facility.longitude,
            )
            return RouteResult(
                distance_m=distance_m,
                estimated_time_s=int(distance_m / self._walking_speed_mps),
                path=[(origin_lat, origin_lon), (facility.latitude, facility.longitude)],
                source="straight_line_estimate",
            )
