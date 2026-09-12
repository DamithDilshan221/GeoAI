"""promote_model.py — Phase 16 operational script.

Reads a Phase 15 manifest, registers the model in ``ml_model_versions``,
and — only if ``evaluation_metrics.beats_heuristic`` is true — promotes it
to active, atomically demoting whatever row was previously active.

Usage:
    # From backend/ with the venv active:
    python -m app.scripts.promote_model <path/to/manifest.json>

This is a manually-run operational script (matching the seed-script pattern
from Phase 3/9), not an HTTP endpoint.  See §16 resolved decision #1.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def _require_fields(manifest: dict, *field_paths: str) -> None:
    """Fail with a clear message naming the first missing field rather than KeyError."""
    for path in field_paths:
        parts = path.split(".")
        obj = manifest
        for part in parts:
            if not isinstance(obj, dict) or part not in obj:
                print(
                    f"ERROR: Required field '{path}' is missing from the manifest.",
                    file=sys.stderr,
                )
                sys.exit(1)
            obj = obj[part]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Register and optionally promote a trained ML model (Phase 16)."
    )
    parser.add_argument("manifest", help="Path to the §15.11 JSON manifest file.")
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"ERROR: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    # ── 1. Load and validate manifest ────────────────────────────────────────
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Manifest is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    _require_fields(
        manifest,
        "version",
        "algorithm",
        "trained_at",
        "feature_list",
        "artifact_path",
        "evaluation_metrics.mae",
        "evaluation_metrics.beats_heuristic",
    )

    version: str = manifest["version"]
    algorithm: str = manifest["algorithm"]
    trained_at: datetime = datetime.fromisoformat(manifest["trained_at"])
    feature_list: list[str] = manifest["feature_list"]
    artifact_path_str: str = manifest["artifact_path"]
    evaluation_metrics: dict = manifest["evaluation_metrics"]
    beats_heuristic: bool = bool(evaluation_metrics["beats_heuristic"])

    print(f"Manifest loaded: version={version}, algorithm={algorithm}")
    print(f"beats_heuristic={beats_heuristic}, MAE={evaluation_metrics['mae']:.4f}")

    # ── 2. Validate artifact exists and loads ─────────────────────────────────
    artifact_path = Path(artifact_path_str)
    if not artifact_path.exists():
        print(
            f"ERROR: Artifact file not found: {artifact_path}\n"
            "The manifest references a file that does not exist. "
            "Re-run training.persist to regenerate it.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import joblib  # noqa: PLC0415
        # Try to load; if sklearn is absent joblib raises ImportError for the pipeline object.
        # In that case we fall back to verifying the file is a valid pickle (sufficient for
        # Phase 16's structural validation goal — not re-running inference).
        try:
            joblib.load(artifact_path)
        except (ImportError, ModuleNotFoundError):
            # sklearn not in backend venv — validate file is a non-empty valid pickle header
            _PICKLE_MAGIC = b"\x80"
            with artifact_path.open("rb") as fh:
                header = fh.read(2)
            if not header.startswith(_PICKLE_MAGIC):
                print(
                    f"ERROR: Artifact file appears corrupt (bad pickle header): {artifact_path}",
                    file=sys.stderr,
                )
                sys.exit(1)
        print(f"Artifact validated: {artifact_path.name}")
    except Exception as exc:
        print(f"ERROR: Failed to validate artifact — {exc}", file=sys.stderr)
        sys.exit(1)

    # ── 3. Database session ───────────────────────────────────────────────────
    from app.core.database import SessionLocal  # noqa: PLC0415
    from app.repositories.ml_model_version_repository import (  # noqa: PLC0415
        MLModelVersionRepository,
        VersionAlreadyExistsError,
        VersionNotFoundError,
    )

    with SessionLocal() as session:
        repo = MLModelVersionRepository(session)

        # ── 4. Idempotent rerun guard (resolved decision #4) ─────────────────
        if repo.exists(version):
            print(
                f"\nalready registered, skipping "
                f"(version='{version}' already in ml_model_versions)."
            )
            sys.exit(0)

        # ── 5. Register (always is_active=false — resolved decision #2) ──────
        try:
            repo.create_version(
                version=version,
                algorithm=algorithm,
                trained_at=trained_at,
                feature_list=feature_list,
                evaluation_metrics=evaluation_metrics,
                artifact_path=artifact_path_str,
            )
            session.commit()
            print(f"\nRegistered version='{version}' with is_active=false (audit trail).")
        except VersionAlreadyExistsError as e:
            # Race-condition guard — create_version raises this; we already
            # checked repo.exists() above but a concurrent insert is possible.
            print(f"\nalready registered, skipping ({e}).")
            sys.exit(0)

        # ── 6. Promotion gate ─────────────────────────────────────────────────
        if beats_heuristic:
            try:
                repo.promote(version)
                session.commit()
            except VersionNotFoundError as e:
                # Should never happen — we just inserted — but guard defensively.
                session.rollback()
                print(f"ERROR: Promotion failed unexpectedly — {e}", file=sys.stderr)
                sys.exit(1)

            mae = evaluation_metrics["mae"]
            heuristic_mae = evaluation_metrics.get("heuristic_mae", float("nan"))
            delta = heuristic_mae - mae
            print(
                f"\n{'='*60}\n"
                f"PROMOTED   version='{version}'\n"
                f"  Algorithm : {algorithm}\n"
                f"  Model MAE : {mae:.4f}\n"
                f"  Heuristic : {heuristic_mae:.4f}\n"
                f"  Improvement (Δ MAE): {delta:.4f} lower is better\n"
                f"  heuristic-v0 is now is_active=false\n"
                f"{'='*60}"
            )
        else:
            mae = evaluation_metrics["mae"]
            heuristic_mae = evaluation_metrics.get("heuristic_mae", float("nan"))
            print(
                f"\n{'='*60}\n"
                f"NOT PROMOTED   version='{version}'\n"
                f"  Algorithm : {algorithm}\n"
                f"  Model MAE : {mae:.4f}\n"
                f"  Heuristic : {heuristic_mae:.4f}\n"
                f"  Candidate did not beat the heuristic — per §15.5 the system\n"
                f"  continues on heuristic-v0 (still is_active=true).\n"
                f"  The new row exists in ml_model_versions with is_active=false\n"
                f"  for auditability (§15.12).\n"
                f"{'='*60}"
            )


if __name__ == "__main__":
    main()
