"""Repository for pedestrian network routing via pgRouting."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.campus_path import CampusPath


class RoutingRepository:
    """Handles spatial graph routing operations against the campus_paths table."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def snap_to_nearest_edge(
        self, lat: float, lon: float, accessible_only: bool
    ) -> tuple[int, float] | None:
        """Find the nearest edge to the given coordinates.

        Returns a tuple of (edge_id, fraction) or None if no edge is found.
        The fraction (0.0 to 1.0) represents where along the edge the point projects.
        """
        # Exclude stairs if accessible_only is true
        type_filter = "AND path_type != 'STAIRS'" if accessible_only else ""

        query = text(
            f"""
            SELECT id,
                   ST_LineLocatePoint(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)) AS fraction
            FROM campus_paths
            WHERE is_active = true
              {type_filter}
            ORDER BY geom <-> ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
            LIMIT 1;
            """
        )

        result = self.session.execute(query, {"lat": lat, "lon": lon}).first()
        if not result:
            return None

        return result.id, result.fraction

    def find_shortest_path(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        accessible_only: bool,
    ) -> list[tuple[float, float]] | None:
        """Calculate the shortest path between two points over the pgRouting network.

        Returns a list of (lat, lon) coordinate pairs representing the path,
        or None if no route could be found.
        """
        origin_snap = self.snap_to_nearest_edge(origin_lat, origin_lon, accessible_only)
        dest_snap = self.snap_to_nearest_edge(dest_lat, dest_lon, accessible_only)

        if not origin_snap or not dest_snap:
            return None

        origin_edge_id, origin_fraction = origin_snap
        dest_edge_id, dest_fraction = dest_snap

        type_filter = "AND path_type != ''STAIRS''" if accessible_only else ""

        # Using 1 and 2 as point IDs for origin and destination.
        # pgRouting will internally negate these to -1 and -2 for the virtual nodes.
        origin_pid = 1
        dest_pid = 2
        origin_vid = -1
        dest_vid = -2

        # Points SQL for pgr_withPoints.
        # pid must be positive. pgRouting creates virtual nodes as -pid.
        points_sql = f"""
            SELECT {origin_pid}::bigint AS pid, {origin_edge_id}::bigint AS edge_id, {origin_fraction}::float8 AS fraction
            UNION ALL
            SELECT {dest_pid}::bigint AS pid, {dest_edge_id}::bigint AS edge_id, {dest_fraction}::float8 AS fraction
        """

        edges_sql = f"""
            SELECT id, source, target, cost, reverse_cost
            FROM campus_paths
            WHERE is_active = true
              {type_filter}
        """

        # We construct the geometry of the route by joining the result of pgr_withPoints
        # back to the campus_paths table.
        # Since pgr_withPoints creates virtual edges for the snapped points, edge values
        # might be the original edge IDs or they might be virtual edge IDs.
        # However, it's easier to just pull the vertices. But pgr_withPoints outputs node.
        # If node < 0, it's our virtual points.
        # Actually, extracting geometries from pgr_withPoints is a bit complex. Let's just 
        # get the path as a single LineString using pgr_withPoints and the original geometries.
        # But wait, pgr_withPoints returns `node` and `edge`.
        # When `edge` is positive, it's a real edge, but we only traverse part of it if we
        # start/end on it.
        # Actually, a simpler robust way to get the geometry of the routing result
        # is to fetch the full path geometries. For virtual edges (edge < 0 or modifying existing),
        # pgRouting 3/4 `pgr_withPoints` documentation states that `edge` is the original edge id.
        # We can extract the points from the route using `node` geometries.
        
        # A common pattern is to just select the nodes.
        # But wait, we need the exact coordinates along the path to return a list of lat/lon pairs.
        
        query = text(
            f"""
            WITH route AS (
                SELECT * FROM pgr_withPoints(
                    '{edges_sql}',
                    '{points_sql}',
                    {origin_vid},
                    {dest_vid},
                    directed := true
                )
            ),
            -- route contains seq, path_seq, start_vid, end_vid, node, edge, cost, agg_cost
            -- node can be -1, -2, or a real vertex ID from campus_paths_vertices_pgr.
            -- To get geometries, we can look up node coordinates.
            -- Real nodes:
            real_nodes AS (
                SELECT id, the_geom FROM campus_paths_vertices_pgr
            ),
            virtual_nodes AS (
                SELECT {origin_vid}::bigint AS id,
                       ST_LineInterpolatePoint((SELECT geom FROM campus_paths WHERE id = {origin_edge_id}), {origin_fraction}) AS the_geom
                UNION ALL
                SELECT {dest_vid}::bigint AS id,
                       ST_LineInterpolatePoint((SELECT geom FROM campus_paths WHERE id = {dest_edge_id}), {dest_fraction}) AS the_geom
            ),
            all_nodes AS (
                SELECT id, the_geom FROM real_nodes
                UNION ALL
                SELECT id, the_geom FROM virtual_nodes
            )
            SELECT ST_Y(an.the_geom) AS lat, ST_X(an.the_geom) AS lon
            FROM route r
            JOIN all_nodes an ON r.node = an.id
            ORDER BY r.path_seq;
            """
        )

        # Wait, if pgr_withPoints returns the sequence of nodes, joining to the geometries 
        # of the nodes gives us the waypoints. This is a very clean way to get the path!
        # The path is just the sequence of nodes.

        result = self.session.execute(query).fetchall()

        if not result:
            return None

        return [(row.lat, row.lon) for row in result]
