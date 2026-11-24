from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.config.database import get_database
from app.utils.dependencies import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/chat", tags=["Chat"])

class MessageInput(BaseModel):
    conversation_id: str
    text: str = Field(min_length=1, max_length=4000)

@router.post("/messages", status_code=201)
async def send_message(data: MessageInput, user=Depends(get_current_user)):
    if not ObjectId.is_valid(data.conversation_id): raise HTTPException(400, "Invalid conversation id")
    db = get_database()
    conversation = await db.conversations.find_one({"_id": ObjectId(data.conversation_id), "participant_ids": str(user["_id"])})
    if not conversation: raise HTTPException(404, "Conversation not found")
    doc = {"conversation_id": data.conversation_id, "sender_id": str(user["_id"]), "text": data.text,
           "created_at": datetime.now(timezone.utc), "read": False}
    result = await db.messages.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return serialize(doc)

@router.get("/{conversation_id}/messages")
async def get_messages(conversation_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(conversation_id): raise HTTPException(400, "Invalid conversation id")
    docs = await get_database().messages.find({"conversation_id": conversation_id}).sort("created_at", 1).to_list(500)
    return [serialize(x) for x in docs]
