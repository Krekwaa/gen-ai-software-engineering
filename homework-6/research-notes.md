# Context7 Research Notes

Research was performed on 11 August 2026 through the configured context7 MCP server. The reproducible client is `scripts/query_context7.py`.

## Query 1: FastAPI HTML and POST endpoint patterns

- Search: `FastAPI static HTMLResponse and POST endpoint patterns`
- Resolved context7 library ID: `/websites/fastapi_tiangolo`
- Result used: Declare `response_class=HTMLResponse` on the route so FastAPI returns `text/html` and documents the response correctly; declare the run action with `@app.post`.
- Applied in: `frontend/app.py`, where `/` returns the checked-in dashboard and `/api/run` executes the pipeline.

## Query 2: FastMCP tool and resource decorators

- Search: `FastMCP Python tool and resource decorator patterns`
- Resolved context7 library ID: `/prefecthq/fastmcp`
- Result used: Create one `FastMCP` server instance, register callable operations with `@mcp.tool`, and expose text through a URI-decorated `@mcp.resource("pipeline://summary")` function.
- Applied in: `mcp/server.py`, including `get_transaction_status`, `list_pipeline_results`, and `pipeline://summary`.

## Verification note

The initial documentation calls used legacy aliases `/fastapi/fastapi` and `/jlowin/fastmcp`; context7 redirected them to the exact IDs recorded above. The queries were rerun using those returned IDs before applying and documenting the patterns.

