import sys
from sqlalchemy import text
from app.core.database import engine

def truncate_usage_records():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE usage_records;"))
        print("Successfully truncated usage_records.")

def run_query_6():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT f.audience, round(avg(u.usage_count)::numeric,2) 
            FROM usage_records u 
            JOIN facilities f ON f.id = u.facility_id 
            WHERE u.hour = 10 AND u.day_of_week < 5 
            GROUP BY f.audience;
        """))
        print("\n--- Step 6 Output (Hour 10 Weekday Averages) ---")
        for row in result:
            print(f"{row[0]}: {row[1]}")

def run_query_7():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT f.audience, round(avg(u.usage_count)::numeric,2) 
            FROM usage_records u 
            JOIN facilities f ON f.id = u.facility_id 
            WHERE u.hour = 2 
            GROUP BY f.audience;
        """))
        print("\n--- Step 7 Output (Hour 2 Averages) ---")
        for row in result:
            print(f"{row[0]}: {row[1]}")

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "truncate":
        truncate_usage_records()
    elif action == "query6":
        run_query_6()
    elif action == "query7":
        run_query_7()
