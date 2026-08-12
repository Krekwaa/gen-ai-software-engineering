"""Invoke the custom MCP tools/resource for local verification and evidence."""

import asyncio
import importlib.util
from pathlib import Path

from fastmcp import Client

server_path = Path(__file__).resolve().parents[1] / "mcp" / "server.py"
spec = importlib.util.spec_from_file_location("pipeline_mcp_server", server_path)
server = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(server)
mcp = server.mcp


async def main() -> None:
    async with Client(mcp) as client:
        status = await client.call_tool("get_transaction_status", {"transaction_id": "TXN005"})
        results = await client.call_tool("list_pipeline_results", {})
        summary = await client.read_resource("pipeline://summary")
        print("get_transaction_status(TXN005)")
        print(status.data)
        print("\nlist_pipeline_results() summary")
        print({"total": results.data["total"], "status_counts": results.data["status_counts"]})
        print("\npipeline://summary")
        print(summary[0].text)


if __name__ == "__main__":
    asyncio.run(main())
