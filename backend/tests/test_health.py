"""Smoke test — proves the test harness and health endpoint work.

This is the only test for Phase 1. It exists to verify that:
  1. The FastAPI TestClient can be instantiated from the app factory.
  2. GET /api/v1/health returns 200 with the expected JSON shape.
"""

from fastapi.testclient import TestClient


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """Test the health check endpoint returns 200 OK and connected DB status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_env" in data
    assert data["database"] == "connected"
