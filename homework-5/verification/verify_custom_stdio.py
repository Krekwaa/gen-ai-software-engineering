"""Verify the configured custom server entry point over stdio."""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "custom-mcp-server" / "server.py"


async def main() -> None:
    parameters = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            templates = await session.list_resource_templates()
            tool_result = await session.call_tool("read", {"word_count": 11})
            resource_result = await session.read_resource(
                "lorem://ipsum?word_count=9"
            )

    tool_text = tool_result.content[0].text
    resource_text = resource_result.contents[0].text
    if len(tool_text.split()) != 11 or len(resource_text.split()) != 9:
        raise RuntimeError("Custom stdio server returned an incorrect word count")

    print("Custom MCP stdio verification")
    print(f"Entry point: {SERVER.name}")
    print(f"Tools: {', '.join(tool.name for tool in tools.tools)}")
    print(f"Resource template: {templates.resourceTemplates[0].uriTemplate}")
    print(f"Tool output ({len(tool_text.split())} words): {tool_text}")
    print(f"Resource output word count: {len(resource_text.split())}")
    print("RESULT: PASS")


if __name__ == "__main__":
    asyncio.run(main())
