"""Reproduce the documented context7 research queries over MCP stdio."""

import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server = StdioServerParameters(command="npx.cmd", args=["-y", "@upstash/context7-mcp@latest"])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS", [tool.name for tool in tools.tools])
            queries = [
                ("FastAPI", "FastAPI static HTMLResponse and POST endpoint patterns"),
                ("FastMCP", "FastMCP Python tool and resource decorator patterns"),
            ]
            for library, query in queries:
                resolved = await session.call_tool("resolve-library-id", {"libraryName": library, "query": query})
                text = "\n".join(block.text for block in resolved.content if hasattr(block, "text"))
                print(f"\nRESOLVE {library}\n{text}")
                preferred = "/websites/fastapi_tiangolo" if library == "FastAPI" else "/prefecthq/fastmcp"
                docs = await session.call_tool("query-docs", {"libraryId": preferred, "query": query})
                output = "\n".join(block.text for block in docs.content if hasattr(block, "text"))
                print(f"\nDOCS {preferred}\n{output[:5000]}")


if __name__ == "__main__":
    asyncio.run(main())
