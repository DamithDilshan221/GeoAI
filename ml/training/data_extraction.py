"""Extracts raw usage_records + facilities columns into a DataFrame."""
import pandas as pd
from sqlalchemy import text

from training.db import get_engine

_QUERY = """
    SELECT
        u.facility_id, u.date, u.day_of_week, u.hour, u.usage_count, u.data_source,
        c.code AS category_code, f.audience AS audience_code, f.total_stalls
    FROM usage_records u
    JOIN facilities f ON f.id = u.facility_id
    JOIN categories c ON c.id = f.category_id
    ORDER BY u.facility_id, u.date, u.hour
"""


def extract_usage_dataframe() -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(_QUERY), conn)


def data_source_composition(df: pd.DataFrame) -> dict[str, float]:
    """Logged in every training run per §15.7, regardless of what it finds."""
    return df["data_source"].value_counts(normalize=True).to_dict()
