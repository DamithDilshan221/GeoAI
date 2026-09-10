import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from sqlalchemy import text

from app.core.database import SessionLocal

db = SessionLocal()
# Origin at (0, 0)
origin_snap = db.execute(
    text(
        "SELECT id, ST_LineLocatePoint(geom, ST_SetSRID(ST_MakePoint(0, 0), 4326)) as fraction FROM campus_paths ORDER BY geom <-> ST_SetSRID(ST_MakePoint(0, 0), 4326) LIMIT 1"  # noqa: E501
    )
).first()
# Dest at (60, 80)
dest_snap = db.execute(
    text(
        "SELECT id, ST_LineLocatePoint(geom, ST_SetSRID(ST_MakePoint(60, 80), 4326)) as fraction FROM campus_paths ORDER BY geom <-> ST_SetSRID(ST_MakePoint(60, 80), 4326) LIMIT 1"  # noqa: E501
    )
).first()

print(f"Origin snapped to edge {origin_snap.id} at {origin_snap.fraction}")
print(f"Dest snapped to edge {dest_snap.id} at {dest_snap.fraction}")

origin_edge_id = origin_snap.id
origin_fraction = origin_snap.fraction
dest_edge_id = dest_snap.id
dest_fraction = dest_snap.fraction

edges_sql = "SELECT id, source, target, cost, reverse_cost FROM campus_paths WHERE is_active = true"
points_sql = (
    f"    SELECT -1::bigint AS pid, {origin_edge_id}::bigint AS edge_id, "
    f"{origin_fraction}::float8 AS fraction\n"
    "    UNION ALL\n"
    f"    SELECT -2::bigint AS pid, {dest_edge_id}::bigint AS edge_id, "
    f"{dest_fraction}::float8 AS fraction\n"
)

pgr_query = f"""
    SELECT * FROM pgr_withPoints(
        '{edges_sql}',
        '{points_sql}',
        -1,
        -2,
        directed := true,
        details := true
    )
"""
try:
    res = db.execute(text(pgr_query)).fetchall()
    print(f"pgr_withPoints returned {len(res)} rows")
    for r in res:
        print(r)
except Exception as e:
    print(f"pgr_withPoints failed: {e}")
