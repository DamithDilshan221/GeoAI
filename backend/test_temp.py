import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db_session

def test_unhandled_exception_returns_500_envelope(db_session, monkeypatch) -> None:
    from app.repositories.category_repository import CategoryRepository

    def _raise(self):
        raise RuntimeError("something internal broke")

    monkeypatch.setattr(CategoryRepository, "list_active", _raise)
    
    def override_get_db_session():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/api/v1/categories")
        print(resp.status_code)
        print(resp.json())
