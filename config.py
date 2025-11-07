import os
import dotenv
from agents.extensions.models.litellm_model import LitellmModel

dotenv.load_dotenv()
llm = "deepseek"
if llm == "deepseek":
    llm_model = LitellmModel(model="deepseek/deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
elif llm == "openai":
    llm_model = "gpt-4.1-nano"
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")