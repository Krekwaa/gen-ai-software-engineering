"""Start the official Filesystem MCP and perform a real list_directory call."""

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


HOMEWORK_ROOT = Path(__file__).resolve().parents[1]


async def main() -> None:
    parameters = StdioServerParameters(
        command="cmd",
        args=[
            "/c",
            "npx",
            "-y",
            "@modelcontextprotocol/server-filesystem",
            str(HOMEWORK_ROOT),
        ],
    )

    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool(
                "list_directory", {"path": str(HOMEWORK_ROOT)}
            )

    tool_names = {tool.name for tool in tools.tools}
    if "list_directory" not in tool_names or result.isError:
        raise RuntimeError("Filesystem MCP verification failed")

    text = result.content[0].text
    print("Official Filesystem MCP verification")
    print(f"Allowed directory: {HOMEWORK_ROOT.name} (resolved absolute path verified)")
    print(f"Tools available: {len(tool_names)}")
    print("list_directory result:")
    print(text)
    print("RESULT: PASS")


if __name__ == "__main__":
    asyncio.run(main())
