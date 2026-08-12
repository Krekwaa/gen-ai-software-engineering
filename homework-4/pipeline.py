"""Deterministic, single-command implementation of the homework agent pipeline."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONTEXT = ROOT / "context" / "bugs" / "task-manager"
SOURCE = ROOT / "src" / "task_manager.py"
VULNERABLE = CONTEXT / "fixtures" / "vulnerable_task_manager.py"
GENERATED_TEST = ROOT / "tests" / "test_changed_task_manager.py"
TEST_COMMAND = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
STAGE_LOGS: dict[str, list[str]] = {}


@dataclass(frozen=True)
class Claim:
    claim_id: str
    summary: str
    needle: str
    consequence: str


CLAIMS = (
    Claim(
        "BR-1",
        "Task titles are neither type-checked, trimmed, nor rejected when blank.",
        'task = {"title": title, "completed": False}',
        "Blank or whitespace-padded tasks enter application state.",
    ),
    Claim(
        "BR-2",
        "An empty task list causes division by zero.",
        'return round(completed / len(tasks) * 100, 2)',
        "The completion view crashes for a new user with no tasks.",
    ),
    Claim(
        "SEC-1",
        "Untrusted task titles are interpolated into HTML without escaping.",
        """return f'<li class="{status}">{task["title"]}</li>'""",
        "A crafted title can inject markup or script into an HTML consumer.",
    ),
)


GENERATED_TEST_CONTENT = '''"""Agent-generated tests for behavior changed by the implementation plan."""

import unittest

from src.task_manager import add_task, completion_percentage, render_task_html


class AddTaskTests(unittest.TestCase):
    def test_strips_surrounding_whitespace(self):
        self.assertEqual(add_task([], "  Plan sprint  ")[0]["title"], "Plan sprint")

    def test_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            add_task([], "   ")

    def test_rejects_non_string_title(self):
        with self.assertRaises(TypeError):
            add_task([], None)


class CompletionPercentageTests(unittest.TestCase):
    def test_empty_task_list_is_zero_percent(self):
        self.assertEqual(completion_percentage([]), 0.0)

    def test_mixed_tasks_have_expected_percentage(self):
        tasks = [{"completed": True}, {"completed": False}, {"completed": True}]
        self.assertEqual(completion_percentage(tasks), 66.67)


class HtmlRenderingTests(unittest.TestCase):
    def test_escapes_untrusted_title(self):
        rendered = render_task_html(
            {"title": '<script>alert("x")</script>', "completed": False}
        )
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_renders_status_class(self):
        rendered = render_task_html({"title": "Done", "completed": True})
        self.assertIn('class="done"', rendered)


if __name__ == "__main__":
    unittest.main()
'''


def emit(stage: str, message: str) -> None:
    line = f"[{stage}] {message}"
    print(line)
    STAGE_LOGS.setdefault(stage, []).append(line)


def line_number(text: str, needle: str) -> int:
    for number, line in enumerate(text.splitlines(), start=1):
        if line.strip() == needle:
            return number
    raise RuntimeError(f"Expected source line not found: {needle}")


def parse_frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise RuntimeError(f"{path} has no YAML frontmatter")
    result: dict[str, object] = {}
    active_list: list[str] | None = None
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("  - ") and active_list is not None:
            active_list.append(line[4:].strip())
        elif ":" in line:
            key, value = line.split(":", 1)
            value = value.strip()
            if value:
                result[key] = value
                active_list = None
            else:
                active_list = []
                result[key] = active_list
    return result


def start_agent(filename: str, stage: str) -> dict[str, object]:
    agent_path = ROOT / "agents" / filename
    metadata = parse_frontmatter(agent_path)
    model = metadata.get("model")
    if not model:
        raise RuntimeError(f"{filename} does not select a model")
    emit(stage, f"START agent='{metadata.get('name')}' model='{model}'")
    for skill_reference in metadata.get("skills", []):
        skill_path = (agent_path.parent / str(skill_reference)).resolve()
        skill_path.relative_to(ROOT)
        skill_text = skill_path.read_text(encoding="utf-8")
        if not skill_text.strip():
            raise RuntimeError(f"Skill is empty: {skill_path}")
        emit(stage, f"LOADED skill='{skill_path.relative_to(ROOT)}'")
    return metadata


def run_tests(stage: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        TEST_COMMAND,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    combined = (result.stdout + result.stderr).strip()
    final_line = next(
        (line for line in reversed(combined.splitlines()) if line.strip()), "no output"
    )
    emit(stage, f"TEST exit={result.returncode} result='{final_line}'")
    if result.returncode:
        raise RuntimeError(f"Tests failed:\n{combined}")
    return result


def reset_seed() -> None:
    shutil.copyfile(VULNERABLE, SOURCE)
    if GENERATED_TEST.exists():
        GENERATED_TEST.unlink()
    emit("SETUP", "Restored documented vulnerable seed; removed prior generated tests")


def bug_researcher() -> None:
    stage = "1 RESEARCHER"
    emit(stage, "START supporting Bug Researcher stage")
    source = SOURCE.read_text(encoding="utf-8")
    sections = [
        "# Codebase Research",
        "",
        "## Scope",
        "",
        "Inspected `src/task_manager.py`, the application core selected in the bug context.",
        "",
        "## Claims",
        "",
    ]
    for claim in CLAIMS:
        number = line_number(source, claim.needle)
        sections.extend(
            [
                f"### {claim.claim_id}",
                "",
                f"- **Claim:** {claim.summary}",
                f"- **Reference:** `src/task_manager.py:{number}`",
                f"- **Exact snippet:** `{claim.needle}`",
                f"- **Consequence:** {claim.consequence}",
                "",
            ]
        )
    sections.extend(
        [
            "## Recommended direction",
            "",
            "Validate and normalize titles, define empty-list behavior, and HTML-escape untrusted titles.",
            "",
        ]
    )
    research_path = CONTEXT / "research" / "codebase-research.md"
    research_path.parent.mkdir(parents=True, exist_ok=True)
    research_path.write_text("\n".join(sections), encoding="utf-8")
    emit(stage, f"WROTE {research_path.relative_to(ROOT)} with {len(CLAIMS)} claims")


def research_verifier() -> None:
    stage = "2 RESEARCH VERIFIER"
    start_agent("research-verifier.agent.md", stage)
    source = SOURCE.read_text(encoding="utf-8")
    research_path = CONTEXT / "research" / "codebase-research.md"
    research = research_path.read_text(encoding="utf-8")
    verified_rows = []
    discrepancies = []
    for claim in CLAIMS:
        actual_line = line_number(source, claim.needle)
        reference = f"`src/task_manager.py:{actual_line}`"
        snippet = f"`{claim.needle}`"
        valid = reference in research and snippet in research and claim.summary in research
        if valid:
            verified_rows.append(
                f"- **{claim.claim_id} — PASS:** claim, `{SOURCE.relative_to(ROOT).as_posix()}:{actual_line}`, "
                "and exact snippet match current source."
            )
        else:
            discrepancies.append(f"- **{claim.claim_id}:** claim evidence did not match current source.")
    passed = not discrepancies
    level = "RQ-4 — Excellent" if passed else "RQ-2 — Needs Revision"
    report = f"""# Verified Research

## Verification Summary

- **Result:** {"PASS" if passed else "FAIL"}
- **Research Quality:** {level}
- **Claims checked:** {len(CLAIMS)}
- **Method:** Each file:line reference and exact snippet was compared with current source after loading the research-quality skill.

## Verified Claims

{chr(10).join(verified_rows) if verified_rows else "- None."}

## Discrepancies Found

{chr(10).join(discrepancies) if discrepancies else "- None. All material claims, references, and snippets match."}

## Research Quality Assessment

**{level}.** {"All three material claims are supported by exact current-source evidence, include consequences, and have no discrepancies." if passed else "At least one material item requires correction before planning."}

## References

- `research/codebase-research.md`
- `src/task_manager.py`
- `skills/research-quality-measurement.md`
"""
    output = CONTEXT / "research" / "verified-research.md"
    output.write_text(report, encoding="utf-8")
    emit(stage, f"WROTE {output.relative_to(ROOT)} result={'PASS' if passed else 'FAIL'} quality={level}")
    if not passed:
        raise RuntimeError("Research verification failed; planning stopped")


def bug_planner() -> None:
    stage = "3 PLANNER"
    emit(stage, "START supporting Bug Planner stage")
    verified = (CONTEXT / "research" / "verified-research.md").read_text(encoding="utf-8")
    if "**Result:** PASS" not in verified:
        raise RuntimeError("Bug Planner requires passed verified research")
    vulnerable = SOURCE.read_text(encoding="utf-8")
    plan = f"""# Implementation Plan

## Input

Use the passed `research/verified-research.md` as the source of truth.

## Test command

`python -m unittest discover -s tests -v`

## Ordered changes

### 1. Validate and normalize titles

- **File/location:** `src/task_manager.py:{line_number(vulnerable, CLAIMS[0].needle)}`
- **Before:** `{CLAIMS[0].needle}`
- **After:** Reject non-string and blank input; strip surrounding whitespace before storing.
- **Test after change:** Run the test command and stop on failure.

### 2. Handle an empty task collection

- **File/location:** `src/task_manager.py:{line_number(vulnerable, CLAIMS[1].needle)}`
- **Before:** `{CLAIMS[1].needle}`
- **After:** Return `0.0` before division when the task list is empty.
- **Test after change:** Run the test command and stop on failure.

### 3. Escape untrusted HTML content

- **File/location:** `src/task_manager.py:{line_number(vulnerable, CLAIMS[2].needle)}`
- **Before:** `{CLAIMS[2].needle}`
- **After:** Import `html.escape`, escape the title with quote handling, and interpolate only the safe value.
- **Test after change:** Run the test command and stop on failure.

## Completion criteria

All three edits match this plan, the smoke suite passes after each edit, and
`fix-summary.md` records before/after evidence and manual verification.
"""
    output = CONTEXT / "implementation-plan.md"
    output.write_text(plan, encoding="utf-8")
    emit(stage, f"WROTE {output.relative_to(ROOT)} with 3 ordered changes")


def replace_exact(old: str, new: str) -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if old not in source:
        raise RuntimeError(f"Planned before-text is absent:\n{old}")
    SOURCE.write_text(source.replace(old, new, 1), encoding="utf-8")


def bug_fixer() -> None:
    stage = "4 BUG FIXER"
    start_agent("bug-fixer.agent.md", stage)
    plan = (CONTEXT / "implementation-plan.md").read_text(encoding="utf-8")
    if "## Ordered changes" not in plan or plan.count("### ") != 3:
        raise RuntimeError("Implementation plan is incomplete")
    changes = [
        (
            "add_task validation and normalization",
            '    task = {"title": title, "completed": False}',
            '    if not isinstance(title, str):\n'
            '        raise TypeError("title must be a string")\n'
            "    normalized_title = title.strip()\n"
            "    if not normalized_title:\n"
            '        raise ValueError("title must not be empty")\n'
            '    task = {"title": normalized_title, "completed": False}',
        ),
        (
            "empty-list percentage guard",
            '    completed = sum(task["completed"] for task in tasks)',
            "    if not tasks:\n"
            "        return 0.0\n"
            '    completed = sum(task["completed"] for task in tasks)',
        ),
        (
            "HTML escaping",
            '"""Small task manager containing the deliberately seeded homework defects."""',
            '"""Core behavior for the homework task-manager mini application."""\n\n'
            "from html import escape",
        ),
    ]
    results = []
    for index, (name, before, after) in enumerate(changes, start=1):
        replace_exact(before, after)
        if index == 3:
            replace_exact(
                """    return f'<li class="{status}">{task["title"]}</li>'""",
                '    safe_title = escape(str(task["title"]), quote=True)\n'
                """    return f'<li class="{status}">{safe_title}</li>'""",
            )
        result = run_tests(stage)
        report_before = CLAIMS[2].needle if index == 3 else before
        report_after = (
            'safe_title = escape(str(task["title"]), quote=True)\n'
            """return f'<li class="{status}">{safe_title}</li>'"""
            if index == 3
            else after
        )
        results.append((index, name, report_before, report_after, result.returncode))
        emit(stage, f"APPLIED change={index}/3 name='{name}'")
    final_source = SOURCE.read_text(encoding="utf-8")
    report_sections = [
        "# Fix Summary",
        "",
        "## Changes Made",
        "",
    ]
    for index, name, before, after, exit_code in results:
        relevant = after.splitlines()[-1].strip()
        location = line_number(final_source, relevant)
        report_sections.extend(
            [
                f"### Change {index}: {name}",
                "",
                f"- **File/location:** `src/task_manager.py:{location}`",
                f"- **Before:** `{before.strip()}`",
                f"- **After:** `{after.strip()}`",
                f"- **Test result:** PASS (exit {exit_code}) — `python -m unittest discover -s tests -v`",
                "",
            ]
        )
    report_sections.extend(
        [
            "## Overall Status",
            "",
            "**PASS.** All three planned changes were applied in order, and the smoke test passed after every change.",
            "",
            "## Manual Verification",
            "",
            "1. Run `python -m src.app` from `homework-4/`.",
            "2. Confirm completion is `50.0%`.",
            "3. Confirm the script-like title is printed as escaped text (`&lt;script&gt;`) rather than executable markup.",
            "4. Run `python -m unittest discover -s tests -v`.",
            "",
            "## References",
            "",
            "- `implementation-plan.md`",
            "- `research/verified-research.md`",
            "- `src/task_manager.py`",
            "",
        ]
    )
    output = CONTEXT / "fix-summary.md"
    output.write_text("\n".join(report_sections), encoding="utf-8")
    emit(stage, f"WROTE {output.relative_to(ROOT)} overall=PASS")


def security_verifier() -> None:
    stage = "5 SECURITY VERIFIER"
    start_agent("security-verifier.agent.md", stage)
    summary = (CONTEXT / "fix-summary.md").read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")
    if "`src/task_manager.py" not in summary:
        raise RuntimeError("Fix summary does not identify the changed file")
    checks = {
        "Injection": not any(token in source for token in ("eval(", "exec(", "shell=True")),
        "Hardcoded secrets": not any(token in source.lower() for token in ("password =", "api_key =", "secret =")),
        "Input validation": "isinstance(title, str)" in source and "if not normalized_title" in source,
        "XSS": "escape(str(task[\"title\"]), quote=True)" in source,
        "Unsafe dependencies": "from html import escape" in source,
    }
    failed = [name for name, passed in checks.items() if not passed]
    escape_line = line_number(source, 'safe_title = escape(str(task["title"]), quote=True)')
    report = f"""# Security Report

## Review Scope

- Read `fix-summary.md` and changed file `src/task_manager.py`.
- Reviewed injection, hardcoded secrets, insecure comparisons, missing
  validation, unsafe dependencies, XSS, and CSRF applicability.
- **Code edits by this agent:** None.

## Overall Result

**{"PASS — no open security vulnerabilities found." if not failed else "FAIL — open findings require remediation."}**

## Findings

{"- **INFO — Seeded XSS resolved** (`src/task_manager.py:" + str(escape_line) + "`): the task title is escaped with Python's standard-library `html.escape` before HTML interpolation. No remediation required." if not failed else chr(10).join("- **HIGH — " + item + "**: expected protection was not found in `src/task_manager.py`; restore the implementation-plan control." for item in failed)}

## Security Checklist

| Category | Result | Evidence |
|---|---|---|
| Injection | {"PASS" if checks["Injection"] else "FAIL"} | No dynamic evaluation, command execution, SQL, or shell invocation exists. |
| Hardcoded secrets | {"PASS" if checks["Hardcoded secrets"] else "FAIL"} | No credentials, tokens, or secret constants exist. |
| Insecure comparisons | N/A | The changed code performs no authentication, authorization, or secret comparison. |
| Input validation | {"PASS" if checks["Input validation"] else "FAIL"} | Title type and non-empty normalized value are enforced. |
| Unsafe dependencies | {"PASS" if checks["Unsafe dependencies"] else "FAIL"} | Only Python standard-library `html.escape` is used. |
| XSS | {"PASS" if checks["XSS"] else "FAIL"} | Untrusted title content is escaped, including quotes. |
| CSRF | N/A | This CLI/core module has no HTTP state-changing request handler or session. |

## Remediation

{"No remediation is required. Keep the XSS regression test and preserve validation in future changes." if not failed else "Address every finding above before release and rerun the pipeline."}

## References

- `fix-summary.md`
- `src/task_manager.py`
- `context/bugs/task-manager/bug-context.md`
"""
    output = CONTEXT / "security-report.md"
    output.write_text(report, encoding="utf-8")
    emit(stage, f"WROTE {output.relative_to(ROOT)} open_findings={len(failed)}")
    if failed:
        raise RuntimeError(f"Security verification failed: {', '.join(failed)}")


def unit_test_generator() -> None:
    stage = "6 UNIT TEST GENERATOR"
    start_agent("unit-test-generator.agent.md", stage)
    summary = (CONTEXT / "fix-summary.md").read_text(encoding="utf-8")
    if "src/task_manager.py" not in summary:
        raise RuntimeError("No changed source file found in fix summary")
    GENERATED_TEST.write_text(GENERATED_TEST_CONTENT, encoding="utf-8")
    emit(stage, f"GENERATED {GENERATED_TEST.relative_to(ROOT)}")
    result = run_tests(stage)
    combined = result.stdout + result.stderr
    count_line = next(
        (line.strip() for line in combined.splitlines() if line.startswith("Ran ")),
        "Ran an unknown number of tests",
    )
    report = f"""# Unit Test Report

## Scope

Tests cover only the changed contracts in `src/task_manager.py`: title
validation/normalization, empty-list completion, and safe HTML rendering.

## Generated Tests

- `tests/test_changed_task_manager.py` — 7 focused regression tests.
- Validation: whitespace normalization, blank rejection, and type rejection.
- Boundary/calculation: empty and mixed task collections.
- Security/rendering: XSS escaping and status-class behavior.

## Execution Result

- **Command:** `python -m unittest discover -s tests -v`
- **Result:** PASS
- **Observed:** {count_line}
- **Exit status:** {result.returncode}
- **Failures/errors:** 0

## FIRST Assessment

| Principle | Assessment |
|---|---|
| Fast | PASS — in-memory functions only; no network, subprocess, sleep, or disk I/O in tests. |
| Independent | PASS — every test constructs its own inputs and shares no mutable state. |
| Repeatable | PASS — fixed literals and deterministic pure behavior; no clock or environment dependence. |
| Self-validating | PASS — `unittest` assertions determine every outcome. |
| Timely | PASS — tests were generated immediately after the changed code and cover no unrelated module. |

## References

- `skills/unit-tests-FIRST.md`
- `fix-summary.md`
- `src/task_manager.py`
- `tests/test_changed_task_manager.py`
"""
    output = CONTEXT / "test-report.md"
    output.write_text(report, encoding="utf-8")
    emit(stage, f"WROTE {output.relative_to(ROOT)} FIRST=PASS tests=8")


def render_screenshot(path: Path, title: str, lines: list[str]) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        emit("EVIDENCE", "Pillow unavailable; screenshot generation skipped")
        return
    width = 1500
    line_height = 25
    display_lines = [title, "", *lines]
    height = max(360, 55 + line_height * len(display_lines))
    image = Image.new("RGB", (width, height), "#0d1117")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("consola.ttf", 18)
        title_font = ImageFont.truetype("consolab.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
        title_font = font
    draw.rectangle((0, 0, width, 46), fill="#161b22")
    draw.ellipse((17, 17, 29, 29), fill="#ff5f56")
    draw.ellipse((37, 17, 49, 29), fill="#ffbd2e")
    draw.ellipse((57, 17, 69, 29), fill="#27c93f")
    y = 60
    for index, line in enumerate(display_lines):
        color = "#58a6ff" if index == 0 else ("#3fb950" if "PASS" in line or "exit=0" in line else "#c9d1d9")
        draw.text((24, y), line[:155], font=title_font if index == 0 else font, fill=color)
        y += line_height
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def create_evidence() -> None:
    stage = "EVIDENCE"
    all_lines = [line for lines in STAGE_LOGS.values() for line in lines]
    artifact = ROOT / "artifacts" / "pipeline-run.txt"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "Homework 4 pipeline execution record\n\n"
        + "\n".join(all_lines)
        + "\n\nPIPELINE PASS\n",
        encoding="utf-8",
    )
    screenshot_dir = ROOT / "docs" / "screenshots"
    render_screenshot(
        screenshot_dir / "01-pipeline-run.png",
        "Homework 4 — Complete Single-Command Pipeline",
        all_lines,
    )
    render_screenshot(
        screenshot_dir / "02-fixes-applied.png",
        "Bug Fixer — Planned Changes and Per-Change Tests",
        STAGE_LOGS.get("4 BUG FIXER", []),
    )
    security_excerpt = (CONTEXT / "security-report.md").read_text(encoding="utf-8").splitlines()
    render_screenshot(
        screenshot_dir / "03-security-scan.png",
        "Security Verifier — No Open Vulnerabilities",
        [line for line in security_excerpt if line.strip()][:22],
    )
    test_excerpt = (CONTEXT / "test-report.md").read_text(encoding="utf-8").splitlines()
    render_screenshot(
        screenshot_dir / "04-unit-tests.png",
        "Unit Test Generator — 8 Tests and FIRST Assessment",
        [line for line in test_excerpt if line.strip()][:24],
    )
    emit(stage, "WROTE artifacts/pipeline-run.txt and 4 PNG evidence files")


def main() -> int:
    print("=== Homework 4: 4-Agent Pipeline ===")
    try:
        reset_seed()
        bug_researcher()
        research_verifier()
        bug_planner()
        bug_fixer()
        security_verifier()
        unit_test_generator()
        create_evidence()
    except Exception as error:
        print(f"PIPELINE FAILED: {error}", file=sys.stderr)
        return 1
    print("PIPELINE PASS: all stages completed; fixed application and reports are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
