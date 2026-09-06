"""Smoke test — proves the test harness and health endpoint work.

This is the only test for Phase 1. It exists to verify that:
  1. The FastAPI TestClient can be instantiated from the app factory.
  2. GET /api/v1/health returns 200 with the expected JSON shape.
"""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_ok():
    """GET /api/v1/health should return 200 with status 'ok'."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "app_env" in body
