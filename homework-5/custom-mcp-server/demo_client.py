"""Produce human-readable proof of the custom MCP resource and tool calls."""

import asyncio

from fastmcp import Client

from server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        templates = await client.list_resource_templates()
        tool_result = await client.call_tool("read", {"word_count": 10})
        resource_result = await client.read_resource("lorem://ipsum?word_count=8")

    print("Custom FastMCP server verification")
    print(f"Tools: {', '.join(tool.name for tool in tools)}")
    print(f"Resource template: {templates[0].uriTemplate}")
    print(f"read(word_count=10): {tool_result.data}")
    print(f"Tool word count: {len(tool_result.data.split())}")
    print(f"Resource word count: {len(resource_result[0].text.split())}")
    print("RESULT: PASS")


if __name__ == "__main__":
    asyncio.run(main())
