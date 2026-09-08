"""Domain service orchestrating pedestrian routing."""

from typing import Literal

from app.core.config import get_settings
from app.domain.entities import RouteResult
from app.domain.gis.coordinate_validation import validate_coordinates
from app.domain.gis.distance_estimation import estimate_distance_m
from app.repositories.facility_repository import FacilityRepository
from app.repositories.routing_repository import RoutingRepository


class PedestrianRoutingService:
    """Orchestrates pedestrian routing between an origin and a facility."""

    def __init__(
        self,
        routing_repo: RoutingRepository,
        facility_repo: FacilityRepository,
    ) -> None:
        self.routing_repo = routing_repo
        self.facility_repo = facility_repo

    def get_route(
        self, origin_lat: float, origin_lon: float, facility_id: int, accessible_only: bool
    ) -> RouteResult | None:
        """Calculate the shortest pedestrian route to a facility.

        Returns a RouteResult or None if the facility does not exist or is inactive.
        """
        # Validate origin
        validate_coordinates(lat=origin_lat, lon=origin_lon)

        # Fetch facility
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility or not facility.is_active:
            return None

        # Try to find path using pgRouting network
        path = self.routing_repo.find_shortest_path(
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            dest_lat=facility.latitude,
            dest_lon=facility.longitude,
            accessible_only=accessible_only,
        )

        settings = get_settings()

        if path is not None and len(path) >= 2:
            source: Literal["network", "straight_line_estimate"] = "network"
            
            # We have the path points. To calculate accurate distance, we sum the haversine 
            # distance between consecutive path points.
            # (In a real system, the repository might return the pgRouting agg_cost, but doing it
            # here ensures exact meter calculations that match the returned path).
            total_distance = 0.0
            for i in range(len(path) - 1):
                p1_lat, p1_lon = path[i]
                p2_lat, p2_lon = path[i + 1]
                total_distance += estimate_distance_m(
                    origin_lat=p1_lat,
                    origin_lon=p1_lon,
                    dest_lat=p2_lat,
                    dest_lon=p2_lon,
                )
        else:
            # Fallback to straight line
            source = "straight_line_estimate"
            total_distance = estimate_distance_m(
                origin_lat=origin_lat,
                origin_lon=origin_lon,
                dest_lat=facility.latitude,
                dest_lon=facility.longitude,
            )
            path = [(origin_lat, origin_lon), (facility.latitude, facility.longitude)]

        # Estimate time based on distance and configuration.
        # Since we just sum the total distance and the routing algorithm did not track speed per edge,
        # we'll use an average or base walking speed.
        # In a more advanced implementation, the SQL query would compute time per edge based on path_type.
        speed_mps = settings.PEDESTRIAN_WALKING_SPEED_MPS
        estimated_time_s = int(total_distance / speed_mps) if speed_mps > 0 else 0

        return RouteResult(
            distance_m=total_distance,
            estimated_time_s=estimated_time_s,
            path=path,
            source=source,
        )
