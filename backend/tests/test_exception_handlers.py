"""Integration tests for the global exception handlers (§22.1, §22.2).

Strategy: monkeypatch a repository method to raise, then hit a real endpoint
via the ``client`` fixture — this exercises the actual FastAPI exception-dispatch
path, not just the handler functions in isolation.

The regression guard (test_existing_422_and_404_flows_unaffected) is the most
important test here: it proves the new catch-all does not shadow FastAPI's own
handling of deliberately-raised HTTPExceptions anywhere in the codebase.
"""

import pytest
from fastapi.testclient import TestClient


def test_operational_error_returns_503_envelope(client: TestClient, monkeypatch) -> None:
    """A real SQLAlchemy OperationalError reaches the 503 handler."""
    from app.repositories.category_repository import CategoryRepository
    from sqlalchemy.exc import OperationalError

    def _raise(self):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr(CategoryRepository, "list_active", _raise)

    resp = client.get("/api/v1/categories")

    assert resp.status_code == 503
    body = resp.json()
    assert body["error"] == "The service is temporarily unavailable."
    assert body["request_id"]
    # The request_id must be a valid non-empty string (UUID4 format)
    assert len(body["request_id"]) == 36


def test_unhandled_exception_returns_500_envelope(client: TestClient, monkeypatch) -> None:
    """An unexpected RuntimeError reaches the generic 500 handler.

    Critical: exception message, type name, and traceback must NOT appear in the
    client-facing response body.
    """
    from app.repositories.category_repository import CategoryRepository

    def _raise(self):
        raise RuntimeError("something internal broke")

    monkeypatch.setattr(CategoryRepository, "list_active", _raise)

    resp = client.get("/api/v1/categories")

    assert resp.status_code == 500
    body = resp.json()
    assert body["error"] == "An unexpected error occurred."
    assert body["request_id"]
    # No leak of exception detail into the client body
    assert "something internal broke" not in resp.text
    assert "RuntimeError" not in resp.text
    assert "Traceback" not in resp.text


def test_request_id_differs_across_requests(client: TestClient, monkeypatch) -> None:
    """Each request gets a fresh UUID — they must never be the same."""
    from app.repositories.category_repository import CategoryRepository

    monkeypatch.setattr(
        CategoryRepository,
        "list_active",
        lambda self: (_ for _ in ()).throw(RuntimeError("x")),
    )

    first = client.get("/api/v1/categories").json()["request_id"]
    second = client.get("/api/v1/categories").json()["request_id"]

    assert first != second


def test_existing_422_and_404_flows_unaffected(client: TestClient) -> None:
    """Regression guard: the new catch-all must NOT shadow FastAPI's own,
    already-correct handling of deliberately-raised HTTPExceptions.

    §22.2's "consistent JSON error shape" applies only to genuinely unhandled
    exceptions; it is not a mandate to rewrite the existing, tested 422/404 raises.
    """
    # Coordinate validation 422 - lat=91 is out of range
    resp = client.get("/api/v1/washrooms/nearby?lat=91.0&lon=20.0&category=restroom")
    assert resp.status_code == 422

    # Facility not found 404
    resp2 = client.get("/api/v1/facilities/999999999")
    assert resp2.status_code == 404
