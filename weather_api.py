from fastapi import FastAPI
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
        reply = await agent.get_response(req.message)
        return {
            "user_message": req.message,
            "agent_reply": reply
        }
    except Exception as e:
        return {"error": str(e)}
