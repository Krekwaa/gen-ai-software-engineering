# How to Run Homework 4

## 1. Prerequisites

- Python 3.10 or newer available as `python`
- Optional: Pillow (`PIL`) to regenerate the PNG screenshots. The pipeline,
  application, and tests still work without it.

No virtual environment, package installation, API key, or network connection
is required.

## 2. Run the whole pipeline with one command

From the repository root:

```powershell
cd homework-4
python pipeline.py
```

This one command runs every stage without manual intervention. Expected final
line:

```text
PIPELINE PASS: all stages completed; fixed application and reports are ready.
```

The command intentionally performs these steps:

1. Restore the documented vulnerable fixture to `src/task_manager.py`.
2. Bug Researcher writes `research/codebase-research.md`.
3. Bug Research Verifier loads the research-quality skill and verifies every
   claim, snippet, and file:line reference.
4. Bug Planner creates `implementation-plan.md` from verified research.
5. Bug Fixer applies three changes and runs the smoke test after each one.
6. Security Verifier reviews changed code without editing it.
7. Unit Test Generator loads the FIRST skill, creates focused tests, and runs
   the complete suite.
8. Save the execution artifact and screenshot evidence.

An optional Windows wrapper is also provided where local PowerShell execution
policy permits scripts:

```powershell
.\run-pipeline.ps1
```

## 3. Run the fixed application

From `homework-4/`:

```powershell
python -m src.app
```

Expected output:

```text
Task Manager Demo
Completion: 50.0%
Safe HTML:
  <li class="done">Review agent reports</li>
  <li class="open">&lt;script&gt;alert(&#x27;demo&#x27;)&lt;/script&gt;</li>
```

The first title demonstrates whitespace normalization. The second demonstrates
that script-like input is output as harmless escaped text.

## 4. Run tests independently

```powershell
python -m unittest discover -s tests -v
```

Expected summary:

```text
Ran 8 tests

OK
```

## 5. Inspect the results

Open these files in order:

1. `context/bugs/task-manager/research/codebase-research.md`
2. `context/bugs/task-manager/research/verified-research.md`
3. `context/bugs/task-manager/implementation-plan.md`
4. `context/bugs/task-manager/fix-summary.md`
5. `context/bugs/task-manager/security-report.md`
6. `context/bugs/task-manager/test-report.md`
7. `artifacts/pipeline-run.txt`
8. `docs/screenshots/`

The submitted `src/task_manager.py` is the fixed after-state. The original
seed is retained only as an explicit fixture under
`context/bugs/task-manager/fixtures/`.

## 6. Troubleshooting

- If `python` is not recognized, install Python 3.10+ and enable “Add Python to
  PATH,” or replace `python` with the local Python launcher command.
- If the optional `.ps1` wrapper is blocked by organizational policy, use the
  primary `python pipeline.py` command; do not weaken system execution policy.
- If screenshot generation says Pillow is unavailable, existing submitted
  screenshots remain valid. Install Pillow only if new PNG evidence is needed.
- A nonzero exit stops the pipeline. Read the final error and the last
  generated report; the runner never prints a false PASS after failure.
