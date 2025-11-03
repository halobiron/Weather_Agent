import subprocess
import time
from typing import Any

def start_mcp_server():
    process: subprocess.Popen[Any] | None = None
    try:
        process = subprocess.Popen([
            "python", "-m", "mcp_weather_server",
            "--mode", "sse",
            "--host", "localhost",
            "--port", "4000"
        ])
        time.sleep(3)
        print("Weather Server started at http://localhost:4000/sse\n")
        return process
    except Exception as e:
        print(f"Error starting SSE server: {e}")
        exit(1)