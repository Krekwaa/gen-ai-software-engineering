# Homework 5: Four MCP Server Integrations

> **Student:** Vlad
>
> **Assignment:** Homework 5 — Configure MCP Servers
>
> **Date:** August 4, 2026
>
> **AI assistance:** Codex was used to research current official MCP setup,
> implement and test the custom FastMCP server, exercise the Filesystem and
> GitHub integrations, and prepare reproducible documentation.

## Overview

This submission registers the four required MCP servers for a VS Code + GitHub
Copilot client opened at the `homework-5` folder:

| Server | Implementation | Transport | Authentication/access |
|---|---|---|---|
| GitHub | Official hosted GitHub MCP | HTTP | Interactive GitHub OAuth |
| Filesystem | Official `@modelcontextprotocol/server-filesystem` | stdio | Restricted to `${workspaceFolder}` |
| Notion | Official hosted Notion MCP | HTTP | Interactive Notion OAuth |
| Custom Lorem Reader | Local FastMCP 3.4.5 server | stdio | Local file only |

No access token or password is committed. The submitted `mcp.json` and the
VS Code-discovered `.vscode/mcp.json` contain only official endpoints, local
commands, and workspace-relative paths.

## Custom FastMCP server

The custom server provides:

- Resource template `lorem://ipsum{?word_count}`. Calling
  `lorem://ipsum` returns the default 30 words; the query parameter selects a
  different valid count.
- Tool `read`, with optional integer `word_count=30`, returning exactly that
  many words from `custom-mcp-server/lorem-ipsum.md`.
- Input validation for non-integer, zero/negative, and over-source counts.
- Six tests covering pure behavior and real in-memory MCP tool/resource calls.
- A separate stdio verifier that starts the exact `server.py` entry point used
  by the MCP configuration.

### Resources versus tools

An MCP **resource** is content identified by a URI that the AI client can read,
such as a file, API response, or this parameterized Lorem Ipsum excerpt. An MCP
**tool** is an action the AI can choose to call with arguments, such as the
`read` operation that requests a specific word count.

## Verified results

- Configuration validation: **PASS**, four servers registered and synchronized.
- Custom FastMCP unit/protocol tests: **PASS**, 6 tests.
- Custom stdio startup and calls: **PASS**.
- Official Filesystem MCP startup and `list_directory`: **PASS**, 14 tools exposed.
- Connected GitHub query: **PASS**, five recent repository commits returned.
- Notion endpoint/configuration: **PASS**; user-bound OAuth and real-project
  result must be completed in VS Code for the required screenshot.

See [verification-results.md](docs/verification-results.md) for observed
results and [HOWTORUN.md](HOWTORUN.md) for the complete setup and interaction
workflow.

## Project structure

```text
homework-5/
├── .vscode/mcp.json
├── mcp.json
├── README.md
├── HOWTORUN.md
├── PR-DESCRIPTION.md
├── custom-mcp-server/
│   ├── server.py
│   ├── lorem-ipsum.md
│   ├── requirements.txt
│   ├── demo_client.py
│   └── test_server.py
├── verification/
│   ├── run_all.py
│   ├── verify_configuration.py
│   ├── verify_custom_stdio.py
│   └── verify_filesystem_mcp.py
└── docs/
    ├── verification-results.md
    ├── SCREENSHOT-GUIDE.md
    └── screenshots/
```

## Security notes

- GitHub and Notion use OAuth; tokens are stored by the client, not in Git.
- Filesystem MCP receives only `homework-5` as its allowed directory when that
  folder is opened as the VS Code workspace.
- The custom server reads one fixed file resolved relative to `server.py`; it
  does not accept a caller-supplied path.
- `.gitignore` excludes the virtual environment, `.env`, bytecode, and local
  MCP authentication state.

## References

- [Official GitHub MCP server](https://github.com/github/github-mcp-server)
- [Official Filesystem MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- [Official Notion MCP setup](https://developers.notion.com/guides/mcp/get-started-with-mcp)
- [FastMCP resources and templates](https://gofastmcp.com/v2/servers/resources)
