"""Repository for reading and writing ml_model_versions rows.

Phase 13 established the read side (``get_active_version``).
Phase 16 extends this repository with write methods for model registration
and promotion.  This file remains additive — no pre-existing call sites
are modified.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session


class VersionAlreadyExistsError(Exception):
    """Raised by ``create_version`` when the version string is already registered.

    This is the idempotent-skip signal for ``promote_model.py`` (resolved
    decision #4). Callers should catch this specific exception rather than
    a raw ``IntegrityError``.
    """


class VersionNotFoundError(Exception):
    """Raised by ``promote`` when the requested version is not in the table.

    Promoting an unregistered version is always a caller bug — the script
    must call ``create_version`` first.
    """


class MLModelVersionRepository:
    """Data-access object for the ``ml_model_versions`` table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Phase 13 read (unchanged) ─────────────────────────────────────────

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

    # ── Phase 16 writes ───────────────────────────────────────────────────

    def exists(self, version: str) -> bool:
        """Return True if *version* already has a row in ``ml_model_versions``.

        Used by ``promote_model.py`` for the idempotent-rerun check (resolved
        decision #4): if the script is run twice with the same manifest the
        second run prints "already registered, skipping" rather than raising.
        """
        row = self._session.execute(
            text("SELECT 1 FROM ml_model_versions WHERE version = :v LIMIT 1"),
            {"v": version},
        ).one_or_none()
        return row is not None

    def create_version(
        self,
        *,
        version: str,
        algorithm: str,
        trained_at: datetime,
        feature_list: list[str],
        evaluation_metrics: dict,
        artifact_path: str,
        notes: str | None = None,
    ) -> None:
        """Insert a new row with ``is_active = false`` unconditionally.

        Every trained candidate receives a permanent audit-trail row the moment
        it is registered, regardless of whether it will be promoted (resolved
        decision #2 — insertion and promotion are always two separate steps).

        Raises ``VersionAlreadyExistsError`` — not a raw ``IntegrityError`` —
        when *version* already exists, so callers can distinguish the
        idempotent-skip case from genuine database errors (resolved decision #4).
        """
        if self.exists(version):
            raise VersionAlreadyExistsError(
                f"Version '{version}' is already registered in ml_model_versions. "
                "Use the promote() method to change its active status."
            )

        import json as _json  # noqa: PLC0415

        self._session.execute(
            text(
                "INSERT INTO ml_model_versions "
                "(version, algorithm, trained_at, feature_list, evaluation_metrics, "
                " artifact_path, is_active, notes) "
                "VALUES (:version, :algorithm, :trained_at, "
                "        CAST(:feature_list AS json), "
                "        CAST(:evaluation_metrics AS json), "
                "        :artifact_path, false, :notes)"
            ),
            {
                "version": version,
                "algorithm": algorithm,
                "trained_at": trained_at,
                "feature_list": _json.dumps(feature_list),
                "evaluation_metrics": _json.dumps(evaluation_metrics),
                "artifact_path": artifact_path,
                "notes": notes,
            },
        )
        self._session.flush()

    def promote(self, version: str) -> None:
        """Promote *version* to active in one transaction.

        Execution order (resolved decision #3):
          1. Explicitly deactivate every currently-active row.
          2. Activate the named version.

        The ``uq_ml_model_versions_single_active`` partial unique index is a
        database-level safety net, not the primary enforcement mechanism.
        Application code must not rely on catching that constraint violation
        as its control flow.

        Raises ``VersionNotFoundError`` when *version* has never been registered.
        A failed promotion attempt must not accidentally deactivate the currently
        working active row, so the existence check happens before any UPDATE.
        """
        if not self.exists(version):
            raise VersionNotFoundError(
                f"Version '{version}' does not exist in ml_model_versions. "
                "Call create_version() first."
            )

        # Deactivate whatever is currently active.
        self._session.execute(
            text("UPDATE ml_model_versions SET is_active = false WHERE is_active = true")
        )

        # Activate the requested version.
        self._session.execute(
            text("UPDATE ml_model_versions SET is_active = true WHERE version = :v"),
            {"v": version},
        )
        self._session.flush()

