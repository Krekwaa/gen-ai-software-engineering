# How to Run Homework 6

Run all commands from the `homework-6` directory with Python 3.11 or newer.

## 1. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

Node.js is also required when Codex launches the configured context7 MCP server through `npx.cmd` on Windows.

## 2. Run the pipeline

```powershell
python orchestrator.py
```

Expected summary:

```text
Processed: 8
  held_for_review: 1
  rejected: 2
  settled: 5
```

Final files appear under `shared/results/`; `summary.json` contains the dashboard aggregate.

## 3. Validate without processing

```powershell
python -m pipeline.validator --dry-run
```

This reports six valid and two invalid transactions without running fraud detection or settlement.

## 4. Open the web dashboard

```powershell
python -m uvicorn frontend.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. Use **Run pipeline** to refresh the result set.

## 5. Run tests and the coverage gate

```powershell
python -m pytest
```

`pytest.ini` fails the command below 80%. The verified suite reports 97.84%.

Install the real Git pre-push hook once from the repository root:

```powershell
git config core.hooksPath homework-6/.githooks
```

Every subsequent `git push` runs the same coverage command and blocks the push if tests fail or coverage is below 80%.

## 6. Use the Codex skills

The project-local skills are under `.agents/skills/`:

- `$write-spec`
- `$run-pipeline`
- `$validate-transactions`

Compatibility command prompts are also committed under `.codex/commands/` and `.claude/commands/` for rubric visibility.

## 7. Configure and verify MCP

Add or enable `mcp.json` in your Codex project configuration. It defines both `context7` and `pipeline-status`.

Reproduce the context7 research:

```powershell
python scripts/query_context7.py
```

Verify the custom tools and resource in-process:

```powershell
python scripts/verify_mcp.py
```

The custom server can also be started directly:

```powershell
python mcp/server.py
```

## 8. Review submission artifacts

- Specification: `specification.md`
- Context7 evidence: `research-notes.md`
- Screenshots: `docs/screenshots/`
- Presentation: `docs/presentation.pdf`
- Ready-to-copy PR narrative: `PR-DESCRIPTION.md`

## 9. Run the complete acceptance verifier

```powershell
python verification/run_all.py
```

This standalone test program runs an isolated eight-record pipeline, checks exact decisions and privacy behavior, invokes pytest with the coverage gate, calls both custom MCP tools and the summary resource, and audits the required submission artifacts. It exits non-zero if any verification group fails.
