"""ORM model package — imports every model so Base.metadata is complete.

Alembic's env.py imports ``Base`` from this package, relying on the side-effect
of these imports to register all table mappings in ``Base.metadata``.
"""

from app.models.base import Base
from app.models.campus_path import CampusPath
from app.models.category import Category
from app.models.enums import DataSource, FacilityStatus
from app.models.facility import Facility
from app.models.ml_model_version import MLModelVersion
from app.models.recommendation_log import RecommendationLog
from app.models.usage_record import UsageRecord

__all__ = [
    "Base",
    "CampusPath",
    "Category",
    "DataSource",
    "Facility",
    "FacilityStatus",
    "MLModelVersion",
    "RecommendationLog",
    "UsageRecord",
]
