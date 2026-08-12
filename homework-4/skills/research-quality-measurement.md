# Research Quality Measurement Skill

## Purpose

Use this rubric to give a repeatable quality label to codebase research after
checking claims against the current source.

## Required verification method

1. Open every referenced file.
2. Confirm every cited line number contains the claimed behavior.
3. Compare every quoted snippet exactly with source.
4. Mark unsupported, stale, ambiguous, or incomplete claims as discrepancies.
5. Choose the lowest level whose conditions describe the whole report.

## Quality levels

| Level | Label | Definition |
|---|---|---|
| RQ-4 | Excellent | Every material claim, file:line reference, and snippet is correct; causes and impact are supported; no material discrepancy exists. |
| RQ-3 | Good | All material conclusions are supported, but minor non-material reference or wording discrepancies exist. |
| RQ-2 | Needs Revision | One or more material claims are incomplete, ambiguous, stale, or incorrectly referenced; planning requires correction. |
| RQ-1 | Unreliable | Major claims cannot be verified, evidence is absent, or the report would mislead implementation planning. |

## Required output

`verified-research.md` must contain: Verification Summary (including pass/fail
and the exact level and label), Verified Claims, Discrepancies Found, Research
Quality Assessment (level plus reasoning), and References.
