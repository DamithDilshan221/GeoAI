"""Repository for reading ml_model_versions rows.

Provides a properly-layered alternative to the inline raw-SQL that
``health.py`` and ``provider_factory.py`` already contain (those two
pre-existing call sites are explicitly out of this phase's scope per the
non-goals — see §20.5 / Phase 13 spec).  This file is additive: it
introduces the correct example for new call sites without retrofitting old
ones.
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


class MLModelVersionRepository:
    """Data-access object for the ``ml_model_versions`` table.

    Only the ``get_active_version`` read is needed for Phase 13's logging
    step.  No write methods are exposed — model version management is an
    administrative concern outside this phase's scope.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active_version(self) -> str | None:
        """Return the currently-active ``ml_model_versions.version``, or ``None``.

        The partial unique index ``uq_ml_model_versions_single_active`` on
        ``is_active`` guarantees at most one row satisfies this query.
        Returns ``None`` if somehow no row is active — an anomalous state
        (``provider_factory.py``'s ``RuntimeError`` would have surfaced first
        under normal operation) — so callers must treat ``None`` as a
        degraded-but-non-fatal condition, per resolved decision #4.
        """
        row = self._session.execute(
            text("SELECT version FROM ml_model_versions WHERE is_active = true LIMIT 1")
        ).one_or_none()
        return row.version if row else None
