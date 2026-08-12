# How to Run Homework 5

## 1. Prerequisites

- Python 3.10 or newer
- Node.js and NPX
- VS Code 1.101 or newer with GitHub Copilot Chat
- A GitHub account with access to `Krekwaa/gen-ai-software-engineering`
- A Notion workspace containing a real project and at least five bug pages

Open a PowerShell terminal at the repository root.

## 2. Create the Python environment

```powershell
cd homework-5
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r custom-mcp-server\requirements.txt
```

Do not commit `.venv`; it is ignored.

## 3. Verify all non-OAuth servers

From `homework-5/`:

```powershell
.\.venv\Scripts\python.exe verification\run_all.py
```

The command validates both JSON configurations, runs six custom-server tests,
starts the custom server over stdio, calls its tool and resource, then starts
the official Filesystem MCP server and calls `list_directory`.

Expected final result:

```text
ALL NON-OAUTH CHECKS: PASS
```

NPX downloads the official Filesystem server on first use, so that first run
requires network access. Windows launches it through `cmd /c`, avoiding the
PowerShell `npm.ps1` execution-policy problem.

## 4. Run the custom server directly

```powershell
.\.venv\Scripts\python.exe custom-mcp-server\server.py
```

The process waits for MCP messages on stdio; waiting silently after the startup
banner is normal. Stop a manual run with `Ctrl+C`.

For a visible demonstration instead:

```powershell
.\.venv\Scripts\python.exe custom-mcp-server\demo_client.py
```

## 5. Load the MCP configuration in VS Code

The configuration uses `${workspaceFolder}`, so open **the `homework-5` folder
itself** as the workspace:

```powershell
code .
```

Then:

1. Open the Command Palette with `Ctrl+Shift+P`.
2. Run **MCP: List Servers**.
3. Confirm `github`, `filesystem`, `notion`, and `custom-lorem` are listed.
4. Start each server if it is not already running.
5. For GitHub, complete the GitHub OAuth prompt.
6. For Notion, complete the browser OAuth flow and select the workspace/pages
   the MCP connection may access.
7. Never paste a token into `mcp.json` or a screenshot.

`mcp.json` is the submitted readable configuration; `.vscode/mcp.json` is the
identical VS Code project configuration that is automatically discovered.

## 6. Required interactions

In Copilot Chat, select **Agent** mode and ensure MCP tools are enabled.

### GitHub

```text
Use only the GitHub MCP server. List the five most recent commits in
Krekwaa/gen-ai-software-engineering. Show the short SHA and commit message.
```

The known result begins with `b0775ba — Fix PR screenshot links`.

### Filesystem

```text
Use only the Filesystem MCP server. List the top-level files and directories
in the allowed workspace and briefly identify the custom MCP entry point.
```

The response should include `custom-mcp-server`, `mcp.json`, and `README.md`.

### Notion

Use a real project that has at least five bug pages. If necessary, tag those
pages with `Bug` and give each a non-sensitive identifier such as `BUG-001`.
Then use the assignment's required request:

```text
Use only the Notion MCP server. Give me the pages of the last 5 bugs on the
project. Return only each page's non-sensitive bug number and last-edited date.
```

If fewer than five pages are returned, share the correct project/database with
the Notion MCP connection and verify that five pages are categorized as bugs.

### Custom server

```text
Use only the custom-lorem MCP server. Call the read tool with word_count 30.
Show the returned text and confirm its word count.
```

Optionally prove the resource separately:

```text
Read the MCP resource lorem://ipsum?word_count=12 and confirm that it contains
exactly 12 words.
```

## 7. Capture evidence

Follow [SCREENSHOT-GUIDE.md](docs/SCREENSHOT-GUIDE.md). Each screenshot must
show the prompt, MCP server/tool used, full non-sensitive response, and success
state. Store the four PNG files in `docs/screenshots/` with the exact required
names.

## 8. Final validation

```powershell
.\.venv\Scripts\python.exe verification\run_all.py
git status --short
```

Confirm the four screenshots exist and that `.venv`, tokens, and OAuth data are
not staged. Then use `PR-DESCRIPTION.md` for the homework pull request.
