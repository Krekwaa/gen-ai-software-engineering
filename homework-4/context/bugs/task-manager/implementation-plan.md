# Implementation Plan

## Input

Use the passed `research/verified-research.md` as the source of truth.

## Test command

`python -m unittest discover -s tests -v`

## Ordered changes

### 1. Validate and normalize titles

- **File/location:** `src/task_manager.py:6`
- **Before:** `task = {"title": title, "completed": False}`
- **After:** Reject non-string and blank input; strip surrounding whitespace before storing.
- **Test after change:** Run the test command and stop on failure.

### 2. Handle an empty task collection

- **File/location:** `src/task_manager.py:13`
- **Before:** `return round(completed / len(tasks) * 100, 2)`
- **After:** Return `0.0` before division when the task list is empty.
- **Test after change:** Run the test command and stop on failure.

### 3. Escape untrusted HTML content

- **File/location:** `src/task_manager.py:19`
- **Before:** `return f'<li class="{status}">{task["title"]}</li>'`
- **After:** Import `html.escape`, escape the title with quote handling, and interpolate only the safe value.
- **Test after change:** Run the test command and stop on failure.

## Completion criteria

All three edits match this plan, the smoke suite passes after each edit, and
`fix-summary.md` records before/after evidence and manual verification.
