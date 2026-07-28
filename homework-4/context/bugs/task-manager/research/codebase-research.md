# Codebase Research

## Scope

Inspected `src/task_manager.py`, the application core selected in the bug context.

## Claims

### BR-1

- **Claim:** Task titles are neither type-checked, trimmed, nor rejected when blank.
- **Reference:** `src/task_manager.py:6`
- **Exact snippet:** `task = {"title": title, "completed": False}`
- **Consequence:** Blank or whitespace-padded tasks enter application state.

### BR-2

- **Claim:** An empty task list causes division by zero.
- **Reference:** `src/task_manager.py:13`
- **Exact snippet:** `return round(completed / len(tasks) * 100, 2)`
- **Consequence:** The completion view crashes for a new user with no tasks.

### SEC-1

- **Claim:** Untrusted task titles are interpolated into HTML without escaping.
- **Reference:** `src/task_manager.py:19`
- **Exact snippet:** `return f'<li class="{status}">{task["title"]}</li>'`
- **Consequence:** A crafted title can inject markup or script into an HTML consumer.

## Recommended direction

Validate and normalize titles, define empty-list behavior, and HTML-escape untrusted titles.
