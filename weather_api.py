from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from mcp_weather import start_mcp_server
from agent_weather import WeatherAgent

app = FastAPI(title="SmartWeatherPlanner API")

mcp_process = start_mcp_server()

agent = WeatherAgent()

class AskRequest(BaseModel):
    message: str

@app.post("/ask")
async def ask_weather(req: AskRequest):
    try:
        return StreamingResponse(
            agent.get_response_streamed(req.message),
            media_type="text/event-stream"
        )
    except Exception as e:
        return JSONResponse({"error": str(e)})
