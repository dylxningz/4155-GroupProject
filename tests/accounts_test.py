from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from routers.accounts import router
from schemas.accounts import Account, AccountCreate
import dependencies.database as db
import controllers.accounts as controller
from api import app

app.include_router(router)

def test_get_all_accounts():
    mock_db = MagicMock()

    mock_accounts = [
        Account(id="1", name="Jack", email="123@uncc.edu", password="password"),
        Account(id="2", name="Dylan", email="456@uncc.edu", password='password'),
    ]
    controller.read_all = MagicMock(return_value=mock_accounts)

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test the endpoint
    client = TestClient(app)
    response = client.get("/accounts/")
    assert response.status_code == 200
    response_json = response.json()
    for expected, actual in zip(mock_accounts, response_json):
        assert expected.id == actual["id"]
        assert expected.name == actual["name"]
        assert expected.email == actual["email"]

def test_get_one_account():
    mock_db = MagicMock()

    mock_account = Account(id="1", name="Jack", email="123@uncc.edu", password="password")

    # Configure the mock database to return the mock account
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_account
    mock_db.query.return_value = mock_query

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test the endpoint
    client = TestClient(app)
    response = client.get("/accounts/1")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == mock_account.id
    assert response_json["name"] == mock_account.name
    assert response_json["email"] == mock_account.email

def test_get_account_by_email():
    mock_db = MagicMock()

    mock_account = Account(id="1", name="Jack", email="123@uncc.edu", password="password")

    # Configure the mock database to return the mock account
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_account
    mock_db.query.return_value = mock_query

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test the endpoint
    client = TestClient(app)
    response = client.get("/accounts/email/123@uncc.edu")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == mock_account.id
    assert response_json["name"] == mock_account.name
    assert response_json["email"] == mock_account.email

def test_create_account():
    # Mock database session
    mock_db = MagicMock()

    # Mock account creation
    mock_account = Account(id=1, name="Jack", email="123@uncc.edu", password="password")

    def mock_create_account(db, account_data):
        return Account(
            id=1,
            name=account_data.name,
            email=account_data.email,
            password="password"
        )

    controller.create_account = MagicMock(side_effect=mock_create_account)

    print(mock_account)

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)

    # Mock request payload
    new_account_data = {
        "name": "Jack",
        "email": "123@uncc.edu",
        "password": "password"
    }

    # Send POST request to create an account
    response = client.post("/accounts/", json=new_account_data)

    # Validate response
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == 0
    assert response_json["name"] == mock_account.name
    assert response_json["email"] == mock_account.email

def test_delete_account():
    mock_db = MagicMock()

    mock_account = Account(id="1", name="Jack", email="123@uncc.edu", password="password")

    # Configure the mock database to return the mock account
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_account
    mock_db.query.return_value = mock_query

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test the endpoint
    client = TestClient(app)
    response = client.delete("/accounts/1")
    assert response.status_code == 204

def test_update_account():
    mock_db = MagicMock()

    mock_account = Account(id="1", name="Jack", email="123@uncc.edu", password="password")

    # Configure the mock database to return the mock account
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_account
    mock_db.query.return_value = mock_query

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    new_account_info = {
        "name": "Dylan",
        "email": "456@uncc.edu",
        "password": "password2"
    }

    # Test the endpoint
    client = TestClient(app)
    response = client.put("/accounts/1", json=new_account_info)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == mock_account.id
    assert response_json["name"] == "Dylan"
    assert response_json["email"] == "456@uncc.edu"

def test_login():
    mock_db = MagicMock()

    mock_account = Account(id="1", name="Jack", email="123@uncc.edu", password="password")

    # Configure the mock database to return the mock account
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_account
    mock_db.query.return_value = mock_query

    # Override the get_db dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    account_info = {
        "login": "123@uncc.edu",
        "password": "password",
    }

    # Test the endpoint
    client = TestClient(app)
    response = client.post("/accounts/login", json=account_info)
    assert response.status_code == 422