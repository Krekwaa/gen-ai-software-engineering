# Homework 4 — Four-Agent Bug-Fix Pipeline

## Summary

This PR completes Homework 4 with a runnable four-agent workflow around a
dependency-free Python task manager. A single command restores the documented
vulnerable seed, researches three seeded issues, verifies every research
reference, plans and applies fixes, performs a read-only security review,
generates FIRST-compliant regression tests, and saves reports and screenshots.

Implemented:

- 4 required `*.agent.md` definitions with explicit task-appropriate models;
- research-quality and FIRST skills, loaded automatically by relevant agents;
- 2 intentional functional bugs and 1 intentional XSS issue in the preserved
  before-state;
- fixed application in `src/`;
- research, verification, plan, fix, security, and test artifacts;
- 8 passing tests;
- one-command runner plus complete run documentation;
- 4 PNG screenshots under `docs/screenshots/`.

## How to verify

```powershell
cd homework-4
python pipeline.py
python -m src.app
python -m unittest discover -s tests -v
```

Expected results:

- pipeline ends with `PIPELINE PASS`;
- application shows `Completion: 50.0%` and escaped script-like text;
- test suite reports 8 tests and `OK`;
- security report contains 0 open findings.

Detailed instructions: [HOWTORUN.md](HOWTORUN.md)

## AI tools and workflow

Codex was used to interpret the brief, design the agent/skill contracts,
implement the deterministic pipeline and mini application, execute checks, and
inspect the screenshot evidence. The pipeline itself records selected models,
loaded skills, stage order, real test exit codes, and generated artifacts. I
reviewed the final source, reports, application output, tests, and primary
pipeline screenshot.

## Challenges and resolutions

- The supplied expected-structure example says `homework-5/`; the assignment
  and root repository structure clearly identify this as Homework 4, so all
  work is correctly scoped to `homework-4/`.
- The first compile check found an incorrectly quoted exact-source matcher.
  It was fixed before running the workflow, then compilation and the complete
  pipeline passed.
- To preserve both before/after evidence and a fixed submitted app, the
  vulnerable source is retained as a fixture. Each run restores it, applies
  real changes, and finishes with corrected code.

## Screenshots

### Complete pipeline run

![Complete pipeline](https://raw.githubusercontent.com/Krekwaa/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/01-pipeline-run.png)

### Fixes and tests after each change

![Fix stage](https://raw.githubusercontent.com/Krekwaa/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/02-fixes-applied.png)

### Read-only security verification

![Security report](https://raw.githubusercontent.com/Krekwaa/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/03-security-scan.png)

### Generated tests and FIRST assessment

![Unit tests](https://raw.githubusercontent.com/Krekwaa/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/04-unit-tests.png)
