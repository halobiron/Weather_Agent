from pymongo import AsyncMongoClient
from typing import Optional
from pymongo.server_api import ServerApi

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "chat_demo"

_client: Optional[AsyncMongoClient] = None

async def get_db():
    global _client
    if _client is None:
        _client = AsyncMongoClient(MONGO_URI, server_api=ServerApi("1"))
    await _client.admin.command("ping")
    return _client[MONGO_DB_NAME]