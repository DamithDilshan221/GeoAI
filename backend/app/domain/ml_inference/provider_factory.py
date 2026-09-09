from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.ml_inference.heuristic_provider import HeuristicUsageProvider
from app.domain.ml_inference.provider import UsagePredictionProvider
from app.repositories.facility_repository import FacilityRepository
from app.repositories.usage_record_repository import UsageRecordRepository


def get_active_provider(
    session: Session, usage_repo: UsageRecordRepository, facility_repo: FacilityRepository,
) -> UsagePredictionProvider:
    active_row = session.execute(
        text("SELECT algorithm FROM ml_model_versions WHERE is_active = true LIMIT 1")
    ).one_or_none()

    if active_row is None:
        raise RuntimeError(
            "No active row in ml_model_versions — migration 0003 should have "
            "seeded heuristic-v0. Check alembic upgrade head has been run."
        )

    if active_row.algorithm is None:
        return HeuristicUsageProvider(usage_repo, facility_repo)

    raise NotImplementedError(
        f"Active provider algorithm '{active_row.algorithm}' has no implementation yet — Phase 17"
    )
