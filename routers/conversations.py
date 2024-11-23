from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from schemas import conversations as schema
from controllers import conversations as controller
from typing import List
from models.conversations import Conversation, Message
from schemas.conversations import MessageResponse
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from schemas import conversations as schema
from models.conversations import Conversation, Message
from typing import List, Dict

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)

active_connections: Dict[int, List[WebSocket]] = {}

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    if conversation_id not in active_connections:
        active_connections[conversation_id] = []
    active_connections[conversation_id].append(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            sender_id = data.get("sender_id")
            message_body = data.get("message_body")

            if not sender_id or not message_body:
                print("Invalid message received")
                continue

            new_message = Message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                message_body=message_body
            )
            db.add(new_message)
            db.commit()

            for connection in active_connections[conversation_id]:
                await connection.send_text(json.dumps({
                    "conversation_id": conversation_id,
                    "sender_id": sender_id,
                    "message_body": message_body,
                    "created_at": new_message.created_at.isoformat()
                }))
    except WebSocketDisconnect:
        active_connections[conversation_id].remove(websocket)
        if not active_connections[conversation_id]:
            del active_connections[conversation_id]
        print(f"WebSocket disconnected for conversation {conversation_id}")


@router.post("/", response_model=schema.ConversationResponse)
def create_conversation(request: schema.ConversationCreate, db: Session = Depends(get_db)):
    print(f"Create conversation request: {request}")
    conversation = controller.create_conversation(db, request)
    print(f"Created conversation: {conversation}")
    return conversation

@router.get("/{conversation_id}", response_model=schema.ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.post("/start", response_model=schema.ConversationResponse)
def start_or_get_conversation(request: schema.ConversationCreate, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(
        (Conversation.participant_1 == request.participant_1) &
        (Conversation.participant_2 == request.participant_2) &
        (Conversation.item_id == request.item_id)
    ).first()

    if conversation:
        return conversation

    new_conversation = controller.create_conversation(db, request)
    return new_conversation

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    print(f"Fetching messages for conversation_id: {conversation_id}")
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return messages

@router.get("/user/{user_id}")
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(
        (Conversation.participant_1 == user_id) | (Conversation.participant_2 == user_id)
    ).all()
    return conversations
