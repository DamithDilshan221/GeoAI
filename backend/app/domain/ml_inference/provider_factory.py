"""Provider factory — selects the active `UsagePredictionProvider`.

Phase 10 established the pattern: query `ml_model_versions` fresh on every
call so a Phase 16 promotion takes effect without an app restart.  This phase
adds:
  - Use of `MLModelVersionRepository.get_active_row()` (Phase 16/17 addition)
    instead of inline SQL — needed because `artifact_path` was never selected
    by the original query.
  - `load_model()` from `model_loader` — loads from disk only once per
    distinct version string (the cache handles the "expensive" side).
  - `TrainedModelUsageProvider` construction when `algorithm` is non-NULL.
  - Graceful fallback to `HeuristicUsageProvider` on load failure, with
    structured logging.
"""

from __future__ import annotations

import logging

from app.domain.ml_inference.heuristic_provider import HeuristicUsageProvider
from app.domain.ml_inference.model_loader import load_model
from app.domain.ml_inference.provider import UsagePredictionProvider
from app.domain.ml_inference.trained_model_provider import TrainedModelUsageProvider
from app.repositories.facility_repository import FacilityRepository
from app.repositories.ml_model_version_repository import MLModelVersionRepository
from app.repositories.usage_record_repository import UsageRecordRepository

logger = logging.getLogger(__name__)


def get_active_provider(
    session: object,
    usage_repo: UsageRecordRepository,
    facility_repo: FacilityRepository,
    model_version_repo: MLModelVersionRepository,
) -> UsagePredictionProvider:
    """Return the currently-active provider.

    Queries `ml_model_versions` fresh on every call (cheap) so that a Phase 16
    promotion takes effect without restarting the process.  The actual model
    artifact is loaded from disk at most once per distinct version string via
    `load_model()`'s version-keyed cache.

    Args:
        session:           SQLAlchemy session (passed through but not used by this
                           function itself -- retained for signature stability).
        usage_repo:        Injected usage-record repository.
        facility_repo:     Injected facility repository.
        model_version_repo: Repository for `ml_model_versions`; queried here to
                            avoid duplicating the inline SQL from Phase 10.

    Returns:
        A `HeuristicUsageProvider` when `algorithm IS NULL` (heuristic-v0),
        or a `TrainedModelUsageProvider` wrapping the cached Pipeline when a
        trained model is active.

    Raises:
        RuntimeError: When no `is_active=true` row exists (migration 0003 should
                      have seeded heuristic-v0).
    """
    active = model_version_repo.get_active_row()

    if active is None:
        raise RuntimeError(
            "No active row in ml_model_versions — migration 0003 should have "
            "seeded heuristic-v0. Check alembic upgrade head has been run."
        )

    if active.algorithm is None:
        return HeuristicUsageProvider(usage_repo, facility_repo)

    # Trained-model path: load (or cache-hit) the artifact, fall back to
    # heuristic on any load failure rather than propagating an exception.
    try:
        pipeline = load_model(active.version, active.artifact_path)
    except Exception:
        logger.exception(
            "Failed to load model artifact for version %r (path=%r); "
            "falling back to heuristic for this call.",
            active.version,
            active.artifact_path,
        )
        return HeuristicUsageProvider(usage_repo, facility_repo)

    return TrainedModelUsageProvider(pipeline, active.algorithm, usage_repo)
