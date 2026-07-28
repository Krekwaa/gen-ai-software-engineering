# FIRST Unit Test Skill

## Purpose

Generate focused unit tests for newly changed behavior and assess them against
FIRST.

## FIRST criteria

- **Fast**: use in-memory values; no network, subprocess, sleep, or unnecessary I/O.
- **Independent**: each test creates its own inputs and does not rely on order or shared mutable state.
- **Repeatable**: results are deterministic across machines, time zones, and repeated runs.
- **Self-validating**: assertions decide pass/fail without human inspection.
- **Timely**: tests are created with the implementation change and cover only the changed contract.

## Required workflow

1. Read `fix-summary.md` and each changed file it names.
2. Identify only new or modified behavior.
3. Follow the repository's existing test framework and naming conventions.
4. Generate positive, boundary, validation, and security regression tests where relevant.
5. Run the complete test suite.
6. Write `test-report.md` with scope, test cases, command/result, and a
   Fast/Independent/Repeatable/Self-validating/Timely assessment.
