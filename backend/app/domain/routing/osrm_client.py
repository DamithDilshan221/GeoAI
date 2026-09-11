"""OSRM client — pure, stateless request building and response parsing.

No HTTP client lives here; only the two pure functions the routing service calls,
plus the error type for a no-route OSRM response.

See domain/routing/pedestrian_routing_service.py for the class that wraps these
with an httpx call and a Haversine fallback.
"""

from app.domain.entities import RouteResult


class OSRMNoRouteError(Exception):
    """Raised when OSRM returns an empty or missing ``routes`` array."""


def build_route_request_url(
    base_url: str,
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
) -> str:
    """Build the OSRM /route/v1/foot URL for a two-point walking route.

    Coordinate order in the URL is ``lon,lat`` (OSRM convention).
    No step-parsing on the backend — only the browser's own OSRM client
    needs steps; the backend only needs distance + geometry for scoring/display.
    """
    return (
        f"{base_url}/route/v1/foot/"
        f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        "?overview=full&geometries=geojson&steps=false"
    )


def parse_osrm_route_response(body: dict) -> RouteResult:
    """Parse a raw OSRM JSON response body into a ``RouteResult``.

    Raises ``OSRMNoRouteError`` if ``body['routes']`` is missing or empty.

    GeoJSON coordinates arrive as ``[lon, lat]`` pairs; this function swaps
    them to ``(lat, lon)`` — the convention documented on ``RouteResult.path``.
    Callers never need to think about the swap.
    """
    routes = body.get("routes")
    if not routes:
        raise OSRMNoRouteError("OSRM returned no routes")

    route = routes[0]
    distance_m: float = float(route["distance"])
    duration_s: int = int(route["duration"])
    coords: list[list[float]] = route["geometry"]["coordinates"]

    # Swap [lon, lat] → (lat, lon) per RouteResult.path docstring
    path: list[tuple[float, float]] = [(lat, lon) for lon, lat in coords]

    return RouteResult(
        distance_m=distance_m,
        estimated_time_s=duration_s,
        path=path,
        source="network",
    )
