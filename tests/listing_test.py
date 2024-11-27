from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from routers.listings import router
from schemas.listings import Listing
import dependencies.database as db
import controllers.listings as controller
from api import app

app.include_router(router)

def test_get_all_listings():
    mock_db = MagicMock()

    mock_accounts = [
        Listing(id="1", title="Item1", description="Desc1", price=30, user_id=1),
        Listing(id="2", title="Item2", description="Desc2", price=20, user_id=2),
    ]
    controller.read_all = MagicMock(return_value=mock_accounts)

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test the endpoint
    client = TestClient(app)
    response = client.get("/listings/")
    assert response.status_code == 200
    response_json = response.json()
    for expected, actual in zip(mock_accounts, response_json):
        assert expected.id == actual["id"]
        assert expected.title == actual["title"]
        assert expected.description == actual["description"]
        assert expected.price == actual["price"]
        assert expected.user_id == actual["user_id"]

def test_get_one_account():
    mock_db = MagicMock()

    mock_listing = Listing(id="1", title="Item1", description="Desc1", price=30, user_id=1)

    # Configure the mock database to return the mock account
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_listing
    mock_db.query.return_value = mock_query

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test the endpoint
    client = TestClient(app)
    response = client.get("/listings/1")
    assert response.status_code == 200
    response_json = response.json()
    assert mock_listing.id == response_json["id"]
    assert mock_listing.title == response_json["title"]
    assert mock_listing.description == response_json["description"]
    assert mock_listing.price == response_json["price"]
    assert mock_listing.user_id == response_json["user_id"]

def test_delete_account():
    mock_db = MagicMock()

    mock_listing = Listing(id="1", title="Item1", description="Desc1", price=30, user_id=1)

    # Configure the mock database to return the mock account
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_listing
    mock_db.query.return_value = mock_query

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test the endpoint
    client = TestClient(app)
    response = client.delete("/listings/1")
    assert response.status_code == 200

def test_update_listing():
    mock_db = MagicMock()

    mock_listing = Listing(id="1", title="Item1", description="Desc1", price=30, user_id=1)

    # Configure the mock database to return the mock account
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_listing
    mock_db.query.return_value = mock_query

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    new_account_info = {
        "title": "Item2",
        "description": "Desc2",
        "price": 20
    }

    # Test the endpoint
    client = TestClient(app)
    response = client.put("/listings/1", json=new_account_info)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == mock_listing.id
    assert response_json["title"] == "Item2"
    assert response_json["description"] == "Desc2"
    assert response_json["price"] == 20