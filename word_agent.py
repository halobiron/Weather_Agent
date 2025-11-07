import os
import dotenv

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings

dotenv.load_dotenv()

llm_model = "gpt-4.1-nano"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


class WordAgent:
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.word_server = None
        
        self.agent = Agent(
            name="WordDocumentGenerator",
            instructions=(
                "Bạn là một trợ lý chuyên tạo tài liệu Word chuyên nghiệp. "
                "Khi nhận được prompt từ người dùng, hãy sử dụng MCP Word Server "
                "để tạo một file Word đẹp với định dạng chuyên nghiệp: "
                "- Tiêu đề chính với font lớn, in đậm "
                "- Các phần với heading phù hợp "
                "- Bảng biểu nếu cần "
                "- Định dạng văn bản rõ ràng "
                "- Thêm hình ảnh hoặc biểu đồ nếu phù hợp "
                "Trả về đường dẫn hoặc link tải file Word đã tạo."
            ),
            model=llm_model,
            mcp_servers=[], 
            model_settings=ModelSettings(tool_choice="required"),
        )
    
    async def __aenter__(self):
        self.word_server = MCPServerStreamableHttp(
            name="MCP Word Server",
            params={
                "url": "https://mcp-word.xgeni.vn/mcp",
                "headers": {
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json",
                    "X-Conversation-Id": self.conversation_id
                },
            },
            cache_tools_list=True,
            max_retry_attempts=3,
            client_session_timeout_seconds=30,
        )
        await self.word_server.__aenter__()
        self.agent.mcp_servers = [self.word_server]
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.word_server:
            await self.word_server.__aexit__(exc_type, exc, tb)
    
    async def generate(self, prompt: str) -> str:
        result = await Runner.run(self.agent, prompt)
        return result.final_output
        