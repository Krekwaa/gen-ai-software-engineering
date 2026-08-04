# Manual Screenshot Guide

Use Windows Snipping Tool (`Win+Shift+S`). Screenshots must be captured from
the actual VS Code Copilot MCP interactions; do not use generated mock images.

Before capturing, widen the chat panel, hide notifications and unrelated tabs,
and confirm no access token, email address, private title, or sensitive content
is visible.

## 1. GitHub MCP

- Show the prompt requesting the five recent repository commits.
- Show that the `github` MCP server/tool was called successfully.
- Show short SHAs and commit messages in the response.
- Save as `docs/screenshots/github-mcp-result.png`.

## 2. Filesystem MCP

- Show the prompt requesting the allowed workspace listing.
- Show that the `filesystem` MCP server/tool was used.
- Show `custom-mcp-server`, `mcp.json`, and other top-level entries.
- Save as `docs/screenshots/filesystem-mcp-result.png`.

## 3. Notion MCP

- Show the exact last-five-bugs request.
- Show that `notion` was called successfully.
- Show exactly five non-sensitive page/bug numbers; obscure private names.
- Save as `docs/screenshots/notion-mcp-result.png`.

## 4. Custom MCP

- Show the prompt calling `read` with `word_count=30`.
- Show the `custom-lorem` server and `read` tool invocation.
- Show the returned excerpt and confirmation that it contains 30 words.
- Save as `docs/screenshots/custom-mcp-read-tool-result.png`.

Open all four PNG files before committing and verify that their text is legible.
