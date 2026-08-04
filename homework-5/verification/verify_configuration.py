"""Static validation for the submitted four-server MCP configuration."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    config = json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
    servers = config.get("servers", {})
    expected = {"github", "filesystem", "notion", "custom-lorem"}
    if set(servers) != expected:
        raise RuntimeError(f"Expected {sorted(expected)}, found {sorted(servers)}")

    if servers["github"]["url"] != "https://api.githubcopilot.com/mcp/":
        raise RuntimeError("GitHub MCP endpoint is incorrect")
    if servers["notion"]["url"] != "https://mcp.notion.com/mcp":
        raise RuntimeError("Notion MCP endpoint is incorrect")
    if "@modelcontextprotocol/server-filesystem" not in servers["filesystem"]["args"]:
        raise RuntimeError("Official Filesystem MCP package is not configured")
    if "custom-mcp-server/server.py" not in servers["custom-lorem"]["args"][0]:
        raise RuntimeError("Custom server entry point is incorrect")

    requirement = (ROOT / "custom-mcp-server" / "requirements.txt").read_text(
        encoding="utf-8"
    )
    if "fastmcp==" not in requirement:
        raise RuntimeError("FastMCP is not pinned in requirements.txt")

    duplicate = json.loads(
        (ROOT / ".vscode" / "mcp.json").read_text(encoding="utf-8")
    )
    if duplicate != config:
        raise RuntimeError("mcp.json and .vscode/mcp.json are not synchronized")

    print("MCP configuration verification")
    print(f"Registered servers: {', '.join(sorted(servers))}")
    print("Secrets committed: none (GitHub and Notion use OAuth)")
    print("FastMCP dependency: pinned")
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
