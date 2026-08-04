# Homework 5 — Four MCP Server Integrations

## Summary

This submission configures the official GitHub, Filesystem, and Notion MCP
servers and implements a custom FastMCP Lorem Reader. The custom server exposes
a parameterized resource and a `read` tool that both return exact word-limited
content. OAuth credentials remain outside the repository.

## Implemented

- Official hosted GitHub MCP over HTTP/OAuth.
- Official Filesystem MCP over stdio, restricted to the Homework 5 workspace.
- Official hosted Notion MCP over HTTP/OAuth.
- Custom FastMCP 3.4.5 server with `lorem://ipsum{?word_count}` resource.
- Custom `read(word_count=30)` tool.
- Six custom-server tests plus real stdio verification clients.
- Synchronized `mcp.json` and `.vscode/mcp.json` configurations.
- Manual screenshot instructions and required filenames; screenshot evidence is
  intentionally pending and must be added before final course submission.
- Complete setup, verification, security, and troubleshooting documentation.

## Verification

```powershell
cd homework-5
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r custom-mcp-server\requirements.txt
.\.venv\Scripts\python.exe verification\run_all.py
```

Observed non-OAuth result: `ALL NON-OAUTH CHECKS: PASS`.

- Custom server: 6 tests passed.
- Custom stdio tool/resource calls: passed with exact word counts.
- Filesystem stdio call: passed; 14 tools exposed and workspace listed.
- GitHub query: five repository commits returned.
- Notion query: complete the user-bound OAuth flow and capture five
  non-sensitive bug page identifiers before submitting this PR.

## AI assistance

Codex was used to inspect the assignment, verify current official server
configuration, implement and test the FastMCP service, exercise available MCP
calls, and prepare the documentation. Interactive OAuth authorization and the
final screenshots were performed by the student.

## Security decisions

- No PAT, OAuth token, password, or private Notion content is committed.
- Filesystem access is bounded to `${workspaceFolder}`.
- The custom server accepts a word count, not a caller-controlled file path.
- Virtual environments and local authentication state are ignored by Git.

## Screenshots

### GitHub MCP

![GitHub MCP](docs/screenshots/github-mcp-result.png)

### Filesystem MCP

![Filesystem MCP](docs/screenshots/filesystem-mcp-result.png)

### Notion MCP

![Notion MCP](docs/screenshots/notion-mcp-result.png)

### Custom FastMCP read tool

![Custom MCP](docs/screenshots/custom-mcp-read-tool-result.png)
