from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from routers.conversations import router
from schemas.conversations import ConversationCreate, ConversationResponse, MessageResponse
import dependencies.database as db
from api import app

app.include_router(router)


def test_create_conversation():
    mock_db = MagicMock()

    # Mock input and output
    mock_request = ConversationCreate(participant_1=1, participant_2=2, item_id=3)
    mock_response = {
        "id": 1,
        "participant_1": 1,
        "participant_2": 2,
        "item_id": 3,
        "created_at": datetime.utcnow().isoformat(),
        "messages": []
    }

    # Mock controller response
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = mock_response

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.post("/conversations/", json=mock_request.dict())
    assert response.status_code == 200
    assert response.json() == mock_response


def test_get_conversation():
    mock_db = MagicMock()

    # Mock conversation
    mock_conversation = {
        "id": 1,
        "participant_1": 1,
        "participant_2": 2,
        "item_id": 3,
        "created_at": datetime.utcnow().isoformat(),
        "messages": []
    }

    # Mock query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_conversation
    mock_db.query.return_value = mock_query

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.get("/conversations/1")
    assert response.status_code == 200
    assert response.json() == mock_conversation


def test_get_messages():
    mock_db = MagicMock()

    # Mock messages
    mock_messages = [
        {
            "id": 1,
            "conversation_id": 1,
            "sender_id": 1,
            "message_body": "Hello!",
            "created_at": datetime(2023, 1, 1, 0, 0).isoformat()
        },
        {
            "id": 2,
            "conversation_id": 1,
            "sender_id": 2,
            "message_body": "Hi there!",
            "created_at": datetime(2023, 1, 1, 0, 1).isoformat()
        }
    ]

    # Mock query
    mock_query = MagicMock()
    mock_query.filter.return_value.order_by.return_value.all.return_value = mock_messages
    mock_db.query.return_value = mock_query

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.get("/conversations/1/messages")
    assert response.status_code == 200
    assert response.json() == mock_messages


def test_get_user_conversations():
    mock_db = MagicMock()

    # Mock user conversations
    mock_conversations = [
        {
            "id": 1,
            "participant_1": 1,
            "participant_2": 2,
            "item_id": 3,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        },
        {
            "id": 2,
            "participant_1": 1,
            "participant_2": 3,
            "item_id": 4,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
    ]

    # Mock query
    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = mock_conversations
    mock_db.query.return_value = mock_query

    # Override dependency
    app.dependency_overrides[db.get_db] = lambda: mock_db

    # Test client
    client = TestClient(app)
    response = client.get("/conversations/user/1")
    assert response.status_code == 200
    assert response.json() == mock_conversations
