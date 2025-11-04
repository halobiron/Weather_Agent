import os
import dotenv
from agents import Agent, Runner, SQLiteSession
from openai.types.responses import ResponseTextDeltaEvent
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from agents.extensions.models.litellm_model import LitellmModel

dotenv.load_dotenv()
llm = "deepseek"
if llm == "deepseek":
    llm_model = LitellmModel(model="deepseek/deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
elif llm == "openai":
    llm_model = "gpt-4.1-nano"


class WeatherAgent:
    def __init__(self):
        self.session = SQLiteSession("weather_session")
        self.connected = False 
        self.weather_server = MCPServerSse(
            name="MCP Weather SSE",
            params={"url": "http://localhost:4000/sse"},
        )
        self.location_server = MCPServerSse(
            name="MCP Location SSE",
            params={"url": "http://localhost:4001/sse"},
        )
        self.map_server = MCPServerSse(
            name="OpenStreetMap MCP SSE",
            params={"url": "http://localhost:4002/sse"},
        )

        self.agent = Agent(
            name="SmartWeatherPlanner",
            instructions=(
                "Bạn là một trợ lý thời tiết thông minh. "
                "Khi người dùng hỏi về thời tiết ở đâu đó, "
                "hãy dùng MCP Location Server để lấy dữ liệu vị trí nếu cần. "
                "Sau đó, hãy dùng MCP Weather Server để lấy dữ liệu thời tiết và gợi ý hoạt động phù hợp. "
                "Bạn cũng có thể sử dụng OpenStreetMap MCP Server để lấy thông tin bản đồ nếu cần. "
                "Khi cần tìm kiếm địa điểm gần đó, hãy sử dụng NearbySearch MCP server với location từ MCP Location Server. "
                "Trước khi trả lời về thời tiết của 1 ngày gần đây, "
                "hãy dùng tool 'get_current_datetime' để xác định ngày hôm nay, "
                "rồi tính đúng ngày dựa trên đó."
            ),
            model=llm_model,
            mcp_servers=[self.weather_server, self.location_server, self.map_server],
            model_settings=ModelSettings(tool_choice="required"),
        )

    async def get_response_streamed(self, user_message: str):
        if not self.connected:
            await self.weather_server.__aenter__()
            await self.location_server.__aenter__()
            await self.map_server.__aenter__()
            self.connected = True

        result = Runner.run_streamed(starting_agent=self.agent,
                                        input=user_message,
                                        session=self.session)
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                print(f"\n🔧 Tool call:")
                print(f"  Type: {getattr(event.item, 'type', 'N/A')}")
                print(f"  Output: {getattr(event.item, 'output', 'N/A')}\n")

            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                delta = event.data.delta
                yield delta
