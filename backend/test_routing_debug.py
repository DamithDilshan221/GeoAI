import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
res = db.execute(text("SELECT id, source, target FROM campus_paths")).fetchall()
print("PATHS:", res)
res = db.execute(text("SELECT id, ST_AsText(the_geom) FROM campus_paths_vertices_pgr")).fetchall()
print("VERTICES:", res)
