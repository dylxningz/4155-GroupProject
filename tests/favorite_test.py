from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from routers.favorite import router
from schemas.favorite import FavoriteCreate, FavoriteResponse
from models.favorite import Favorite
import dependencies.database as db
from api import app

app.include_router(router)


def test_add_favorite():
    mock_db = MagicMock()

    # Mock input and output
    mock_request = FavoriteCreate(user_id=1, item_id=10)
    mock_response = {
        "id": 1,
        "user_id": 1,
        "item_id": 10,
    }

    # Mock query to simulate no existing favorite
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    # Simulate adding the new favorite
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = mock_response

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.post("/favorite", json=mock_request.dict())
    assert response.status_code == 200
    assert response.json() == mock_response


def test_add_favorite_conflict():
    mock_db = MagicMock()

    # Mock input
    mock_request = FavoriteCreate(user_id=1, item_id=10)

    # Mock query to simulate an existing favorite
    mock_db.query.return_value.filter_by.return_value.first.return_value = {"id": 1, "user_id": 1, "item_id": 10}

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.post("/favorite", json=mock_request.dict())
    assert response.status_code == 409
    assert response.json() == {"detail": "Item already favorited"}


def test_list_favorites():
    mock_db = MagicMock()

    # Mock output
    mock_favorites = [
        {"id": 1, "user_id": 1, "item_id": 10},
        {"id": 2, "user_id": 1, "item_id": 20},
    ]

    # Mock query
    mock_db.query.return_value.filter.return_value.all.return_value = mock_favorites

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.get("/favorites?user_id=1")
    assert response.status_code == 200
    assert response.json() == mock_favorites


def test_list_favorites_missing_user_id():
    client = TestClient(app)
    response = client.get("/favorites")
    assert response.status_code == 422  # FastAPI validates missing query parameters


def test_remove_favorite():
    mock_db = MagicMock()

    # Mock input
    mock_request = FavoriteCreate(user_id=1, item_id=10)

    # Mock existing favorite
    mock_favorite = {"id": 1, "user_id": 1, "item_id": 10}
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_favorite

    # Mock delete and commit
    mock_db.delete.return_value = None
    mock_db.commit.return_value = None

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.post("/unfavorite", json=mock_request.dict())
    assert response.status_code == 200
    assert response.json() == {"message": "Item unfavorited successfully"}


def test_remove_favorite_not_found():
    mock_db = MagicMock()

    # Mock input
    mock_request = FavoriteCreate(user_id=1, item_id=10)

    # Mock query to simulate no favorite found
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.post("/unfavorite", json=mock_request.dict())
    assert response.status_code == 404
    assert response.json() == {"detail": "Favorite not found"}
