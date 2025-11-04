import subprocess
import time
from typing import Any
import os
def start_process(command: list[str], name: str):
    try:
        proc = subprocess.Popen(command)
        print(f"Started {name}: {' '.join(command)}")
        return proc
    except Exception as e:
        print(f"Error starting {name}: {e}")
        return None
    
def start_mcp_server():
    processes = []
    try:
        weather_cmd = [
            "python", "-m", "mcp_weather_server",
            "--mode", "sse",
            "--host", "localhost",
            "--port", "4000"
        ]
        processes.append(start_process(weather_cmd, "Weather Server"))
        time.sleep(1.5)

        ipinfo_cmd = [
            "uvx", "mcp-proxy", "--port=4001", "--",
            "uvx", "mcp-server-ipinfo"
        ]
        processes.append(start_process(ipinfo_cmd, "Location Server (via proxy)"))
        time.sleep(1.5)
        
        osm_cmd = [
            "uvx", "mcp-proxy", "--port=4002", "--",
            "uvx", "osm-mcp-server"
        ]
        processes.append(start_process(osm_cmd, "OpenStreetMap MCP Server"))
        time.sleep(1.5)
        return processes
    except Exception as e:
        print(f"Error starting SSE server: {e}")
        exit(1)