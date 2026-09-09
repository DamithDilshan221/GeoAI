from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.category_repository import CategoryRepository


def test_list_categories(client: TestClient, db_session: Session) -> None:
    repo = CategoryRepository(db_session)
    repo.create(code="cat1", label="Category 1")
    # create second category but inactive to prove we only return active
    # wait, CategoryRepository.create doesn't take is_active parameter in Phase 3.
    # It defaults to True. We will manually update it for testing.
    c2 = repo.create(code="cat2", label="Category 2")
    from app.models.category import Category as CategoryORM

    row2 = db_session.query(CategoryORM).filter_by(id=c2.id).first()
    row2.is_active = False
    db_session.flush()

    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "cat1"
    assert data[0]["label"] == "Category 1"
    assert "id" in data[0]
