# Verified MCP Results

## Configuration

- Four registered servers: `github`, `filesystem`, `notion`, and
  `custom-lorem`.
- GitHub and Notion use hosted OAuth endpoints; no credentials are stored in
  the repository.
- FastMCP is pinned to `3.4.5`.

## GitHub MCP interaction

The connected GitHub capability successfully returned the five most recent
commits from `Krekwaa/gen-ai-software-engineering`:

1. `b0775ba` — Fix PR screenshot links
2. `a17cca1` — Complete homework 4 agent pipeline
3. `63f46a2` — Complete homework 3 specification package
4. `62a83d3` — Implement homework 2 support ticket system
5. `bc708f4` — Revert GitHub Actions pull request

The final submission screenshot must show the equivalent call through the
configured `github` server inside VS Code Copilot.

## Filesystem MCP interaction

The official `@modelcontextprotocol/server-filesystem` server started over
stdio, exposed 14 tools, and successfully executed `list_directory` against
the restricted `homework-5` directory.

## Custom FastMCP interaction

- Six automated tests pass.
- Tool: `read(word_count=10)` returned exactly 10 words.
- Resource: `lorem://ipsum?word_count=8` returned exactly 8 words.
- A separate stdio client verifies the same entry point used by `mcp.json`.

## Notion MCP interaction

The official endpoint is configured. OAuth authorization and the required
query against the student's real Notion project must be completed interactively
in VS Code because the authorization is user-bound and no Notion workspace was
provided to this build environment.
