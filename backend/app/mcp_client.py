from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
# MCP_URL = os.getenv("BASE")
MCP_URL = "http://localhost:8000/mcp"

async def mcp_tools():
    client = MultiServerMCPClient({
        "fastapi_mcp_tools": {"url": MCP_URL, "transport": "sse"}
    })
    all_tools = await client.get_tools()
    # debug
    for t in all_tools:
        print(f"Loaded tool: {t.name}")

    return all_tools

# asyncio.run(mcp_tools())