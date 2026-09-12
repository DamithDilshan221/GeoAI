"""Version-keyed ML model cache (Phase 17 — §23.1 "loaded once at startup").

The cache resolves the two-requirement tension described in the phase brief:
  - "Which provider is active" is queried fresh from `ml_model_versions` on
    every call to `get_active_provider()` — this lets a Phase 16 promotion
    take effect without an app restart (Phase 10's design intent is preserved).
  - "The deserialized model artifact for a given version" is expensive; it is
    cached here, keyed by version string, so `joblib.load()` is called only
    once per distinct promoted version, not once per request.

When a new version is promoted, `get_active_provider()` receives a new
`version` key on its next call and the new artifact is loaded and cached.
The old entry stays in the dict (small memory cost, avoids reload if the old
version were ever re-promoted -- an edge case, but handled for free).
"""

from __future__ import annotations

import logging

import joblib

logger = logging.getLogger(__name__)

# Module-level version-keyed cache.  Populated lazily by load_model().
# Using a plain dict (not an @lru_cache) so clear_model_cache() can reset it
# without process restart -- required for test isolation.
_MODEL_CACHE: dict[str, object] = {}


def load_model(version: str, artifact_path: str) -> object:
    """Return the deserialized sklearn Pipeline for *version*, loading from disk
    on first access and returning the cached object on subsequent calls.

    Args:
        version:       The `ml_model_versions.version` string -- cache key.
        artifact_path: Absolute path to the `.joblib` file written by
                       `training.persist`.

    Returns:
        The fitted sklearn `Pipeline` object (typed as `object` here to
        avoid a hard sklearn import at the module level -- callers that need
        Pipeline-specific APIs cast as needed).

    Raises:
        Any exception raised by `joblib.load()` (e.g. `FileNotFoundError`,
        `pickle.UnpicklingError`) propagates to the caller.  `provider_factory`
        catches this and falls back to the heuristic.
    """
    if version not in _MODEL_CACHE:
        logger.info(
            "Loading ML model from disk: version=%s path=%s",
            version,
            artifact_path,
        )
        _MODEL_CACHE[version] = joblib.load(artifact_path)
        logger.info("ML model loaded and cached: version=%s", version)
    return _MODEL_CACHE[version]


def clear_model_cache() -> None:
    """Remove all entries from the in-process model cache.

    Used exclusively by tests to reset cache state between runs without
    restarting the process.  Do NOT call this in production code paths.
    """
    _MODEL_CACHE.clear()
