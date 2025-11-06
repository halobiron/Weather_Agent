from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from mcp_weather import start_mcp_server
from agent_weather import WeatherAgent
from chat_repository import get_chats, update_chat, delete_chat

app = FastAPI(title="SmartWeatherPlanner API")

mcp_process = start_mcp_server()
agents: dict[str, WeatherAgent] = {}

def get_or_create_agent(session_id: str) -> WeatherAgent:
    if session_id not in agents:
        agents[session_id] = WeatherAgent(session_id=session_id)
    return agents[session_id]

class AskRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"

class ChatResponse(BaseModel):
    chat_id: str
    session_id: str
    role: str
    text: str
    timestamp: str
    metadata: Dict[str, Any]

class ChatUpdateRequest(BaseModel):
    text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@app.post("/ask")
async def ask_weather(req: AskRequest):
    try:
        agent = get_or_create_agent(req.session_id)
        return StreamingResponse(
            agent.get_response_streamed(req.message),
            media_type="text/event-stream"
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/chats/{session_id}", response_model=List[ChatResponse])
async def get_session_chats(session_id: str, limit: int = 20, skip: int = 0):
    chats = await get_chats(session_id, limit=limit, skip=skip)
    return [ChatResponse(**chat) for chat in chats]

@app.put("/chats/{chat_id}", response_model=dict)
async def update_chat_endpoint(chat_id: str, chat_update: ChatUpdateRequest):
    success = await update_chat(
        chat_id=chat_id,
        new_text=chat_update.text,
        new_metadata=chat_update.metadata
    )
    if not success:
        raise HTTPException(status_code=404, detail="Chat không tồn tại")
    return {"message": "Chat đã được cập nhật thành công"}

@app.delete("/chats/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    success = await delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat không tồn tại")
    return {"message": "Chat đã được xóa thành công"}
