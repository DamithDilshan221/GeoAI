"""Tests for provider_factory.get_active_provider (Phase 17).

Focus areas:
  - Cache: joblib.load called once for two successive calls with same active version.
  - clear_model_cache() forces reload on next call.
  - Missing/corrupt artifact -> HeuristicUsageProvider returned (not exception).
  - algorithm IS NULL -> HeuristicUsageProvider, unchanged from Phase 10.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.domain.ml_inference.heuristic_provider import HeuristicUsageProvider
from app.domain.ml_inference.model_loader import clear_model_cache
from app.domain.ml_inference.provider_factory import get_active_provider
from app.repositories.ml_model_version_repository import ActiveModelRow

# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_repos(active_row):
    """Return mocked usage_repo, facility_repo, and model_version_repo."""
    usage_repo = MagicMock()
    facility_repo = MagicMock()
    model_version_repo = MagicMock()
    model_version_repo.get_active_row.return_value = active_row
    return usage_repo, facility_repo, model_version_repo


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestHeuristicPath:
    def test_algorithm_none_returns_heuristic(self):
        active = ActiveModelRow(
            version="heuristic-v0",
            algorithm=None,
            artifact_path=None,
        )
        usage_repo, facility_repo, model_version_repo = _make_repos(active)
        provider = get_active_provider(None, usage_repo, facility_repo, model_version_repo)
        assert isinstance(provider, HeuristicUsageProvider)

    def test_no_active_row_raises_runtime_error(self):
        usage_repo, facility_repo, model_version_repo = _make_repos(None)
        with pytest.raises(RuntimeError, match="No active row in ml_model_versions"):
            get_active_provider(None, usage_repo, facility_repo, model_version_repo)


class TestModelCache:
    def setup_method(self):
        """Reset cache before each test so load counts start at zero."""
        clear_model_cache()

    def test_two_calls_load_artifact_only_once(self, tmp_path):
        """joblib.load must be called exactly once for two calls with same version."""
        import joblib
        from sklearn.linear_model import Ridge

        # Write a tiny real Pipeline artifact
        from sklearn.pipeline import Pipeline
        fake_pipeline = Pipeline([("est", Ridge())])
        artifact = tmp_path / "model.joblib"
        joblib.dump(fake_pipeline, artifact)

        active = ActiveModelRow(
            version="test-v1",
            algorithm="ridge",
            artifact_path=str(artifact),
        )
        usage_repo, facility_repo, model_version_repo = _make_repos(active)

        load_target = "app.domain.ml_inference.model_loader.joblib.load"
        with patch(load_target, wraps=joblib.load) as mock_load:
            get_active_provider(None, usage_repo, facility_repo, model_version_repo)
            get_active_provider(None, usage_repo, facility_repo, model_version_repo)
            assert mock_load.call_count == 1, (
                f"Expected joblib.load called once, got {mock_load.call_count}"
            )

    def test_clear_cache_forces_reload(self, tmp_path):
        """clear_model_cache() causes the next call to reload from disk."""
        import joblib
        from sklearn.linear_model import Ridge
        from sklearn.pipeline import Pipeline
        fake_pipeline = Pipeline([("est", Ridge())])
        artifact = tmp_path / "model2.joblib"
        joblib.dump(fake_pipeline, artifact)

        active = ActiveModelRow(
            version="test-v2",
            algorithm="ridge",
            artifact_path=str(artifact),
        )
        usage_repo, facility_repo, model_version_repo = _make_repos(active)

        load_target = "app.domain.ml_inference.model_loader.joblib.load"
        with patch(load_target, wraps=joblib.load) as mock_load:
            get_active_provider(None, usage_repo, facility_repo, model_version_repo)
            assert mock_load.call_count == 1
            clear_model_cache()
            get_active_provider(None, usage_repo, facility_repo, model_version_repo)
            assert mock_load.call_count == 2, (
                "clear_model_cache() must force a reload on the next call"
            )


class TestMissingArtifactFallback:
    def setup_method(self):
        clear_model_cache()

    def test_missing_artifact_returns_heuristic_not_exception(self):
        """A non-existent artifact path -> HeuristicUsageProvider, not an exception.

        Log assertion uses patch.object on the module logger rather than caplog
        because caplog propagation is unreliable with asyncio_mode=auto.
        """
        import app.domain.ml_inference.provider_factory as factory_module

        active = ActiveModelRow(
            version="bad-v1",
            algorithm="random_forest",
            artifact_path="/nonexistent/path/model.joblib",
        )
        usage_repo, facility_repo, model_version_repo = _make_repos(active)

        with patch.object(factory_module.logger, "exception") as mock_log:
            provider = get_active_provider(None, usage_repo, facility_repo, model_version_repo)

        assert isinstance(provider, HeuristicUsageProvider)
        # Confirm the failure was logged (not silently swallowed).
        mock_log.assert_called_once()
        log_msg = mock_log.call_args[0][0]
        assert "Failed to load model artifact" in log_msg, (
            f"Expected 'Failed to load model artifact' in log message, got: {log_msg!r}"
        )
