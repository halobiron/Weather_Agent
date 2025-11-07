import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from db import get_db

async def save_chat(conversation_id: str, role: str, text: str, metadata: Optional[Dict[str, Any]] = None):
    db = await get_db()
    chat_doc = {
        "chat_id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "role": role,
        "text": text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {}
    }
    result = await db.chats.insert_one(chat_doc)
    return str(result.inserted_id)

async def get_chats(conversation_id: str, limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
    db = await get_db()
    cursor = db.chats.find({"conversation_id": conversation_id}).skip(skip).limit(limit)
    return [doc async for doc in cursor]

async def update_chat(chat_id: str, new_text: str = None, new_metadata: Optional[Dict[str, Any]] = None):
    db = await get_db()
    update_fields = {}
    if new_text:
        update_fields["text"] = new_text
    if new_metadata is not None:
        update_fields["metadata"] = new_metadata
    result = await db.chats.update_one({"chat_id": chat_id}, {"$set": update_fields})
    return result.modified_count > 0

async def delete_chat(chat_id: str):
    db = await get_db()
    result = await db.chats.delete_one({"chat_id": chat_id})
    return result.deleted_count > 0
