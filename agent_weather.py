import os
import dotenv
from agents import Agent, Runner, SQLiteSession, gen_trace_id, trace
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings

dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


class WeatherAgent:
    def __init__(self):
        self.session = SQLiteSession("weather_session")
        self.connected = False 
        self.mcp_server = MCPServerSse(
            name="MCP Weather SSE",
            params={"url": "http://localhost:4000/sse"},
        )

        self.agent = Agent(
            name="SmartWeatherPlanner",
            instructions=(
                "Bạn là một trợ lý thời tiết thông minh. "
                "Khi người dùng hỏi về thời tiết ở đâu đó, "
                "hãy dùng MCP Weather Server để lấy dữ liệu và gợi ý hoạt động phù hợp. "
                "Trước khi trả lời về thời tiết của 1 ngày gần đây, "
                "hãy dùng tool 'get_current_datetime' để xác định ngày hôm nay, "
                "rồi tính đúng ngày dựa trên đó."
            ),
            mcp_servers=[self.mcp_server],
            model_settings=ModelSettings(tool_choice="required"),
        )

    async def get_response(self, user_message: str) -> str:
        if not self.connected:
            await self.mcp_server.__aenter__()
            self.connected = True

        trace_id = gen_trace_id()
        with trace(workflow_name="SmartWeatherPlanner API", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")

            result = await Runner.run(
                starting_agent=self.agent,
                input=user_message,
                session=self.session,
            )
            return result.final_output or "(Không có phản hồi)"
