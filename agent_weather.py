import os

from agents import Agent, Runner, SQLiteSession, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings

from chat_repository import save_chat
from word_agent import WordAgent
from config import llm_model


class WeatherAgent:
    def __init__(self, conversation_id: str = None):
        self.conversation_id = conversation_id or "weather_session_default"
        self.session = SQLiteSession(f"weather_session_{self.conversation_id}")
        self.connected = False 
        self.weather_server = MCPServerSse(
            name="MCP Weather SSE",
            params={"url": "http://localhost:4000/sse"},
            client_session_timeout_seconds=15,
        )
        self.location_server = MCPServerSse(
            name="MCP Location SSE",
            params={"url": "http://localhost:4001/sse"},
            client_session_timeout_seconds=15,
        )
        self.map_server = MCPServerSse(
            name="OpenStreetMap MCP SSE",
            params={"url": "http://localhost:4002/sse"},
            client_session_timeout_seconds=15,
        )

        self.word_agent = WordAgent(self.conversation_id)

        self.agent = Agent(
            name="SmartWeatherPlanner",
            instructions=(
                "Bạn là một trợ lý thời tiết thông minh. "
                "Trước tiên, luôn dùng MCP Location Server để lấy vị trí hiện tại của người dùng nếu cần. "
                "Khi người dùng hỏi về thời tiết ở đâu đó, "
                "hãy dùng MCP Weather Server để lấy dữ liệu thời tiết và gợi ý hoạt động phù hợp. "
                "Bạn cũng có thể sử dụng OpenStreetMap MCP Server để lấy thông tin bản đồ nếu cần. "
                "Khi cần tìm kiếm địa điểm gần đó, hãy sử dụng NearbySearch MCP server với location từ MCP Location Server. "
                "Trước khi trả lời về thời tiết của 1 ngày gần đây, "
                "hãy dùng tool 'get_current_datetime' để xác định ngày hôm nay, "
                "rồi tính đúng ngày dựa trên đó. "
                "Nếu người dùng yêu cầu tạo báo cáo, tài liệu, hoặc file Word, "
                "hãy sử dụng tool 'generate_word_document' để tạo tài liệu Word chuyên nghiệp."
            ),
            model=llm_model,
            mcp_servers=[self.weather_server, self.location_server, self.map_server],
            tools=[self.word_agent.agent.as_tool(tool_name="generate_word_document",
                   tool_description="Tạo tài liệu Word chuyên nghiệp từ prompt của người dùng.")],
            model_settings=ModelSettings(tool_choice="required",
                                        extra_args={"request_timeout": 5000}),
        )

    async def get_response_streamed(self, user_message: str):
        await save_chat(conversation_id=self.conversation_id, role="user", text=user_message)
        if not self.connected:
            await self.weather_server.__aenter__()
            await self.location_server.__aenter__()
            await self.map_server.__aenter__()
            await self.word_agent.__aenter__()
            self.connected = True
        
        full_response = ""

        result = Runner.run_streamed(starting_agent=self.agent,
                                        input=user_message,
                                        session=self.session)
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                print(f"\n🔧 Tool call:")
                print(f"  Type: {getattr(event.item, 'type', 'N/A')}")
                print(f"  Output: {getattr(event.item, 'output', 'N/A')}\n")
                if event.item.type == "tool_call_item":
                    tool_call = event.item.raw_item
                    f_name = tool_call.name
                    print(f"  Tool Name: {f_name}\n")

            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                delta = event.data.delta
                full_response += delta
                yield delta
                
        await save_chat(conversation_id=self.conversation_id, role="assistant", text=full_response)
