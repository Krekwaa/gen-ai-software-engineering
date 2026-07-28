# Fix Summary

## Changes Made

### Change 1: add_task validation and normalization

- **File/location:** `src/task_manager.py:13`
- **Before:** `task = {"title": title, "completed": False}`
- **After:** `if not isinstance(title, str):
        raise TypeError("title must be a string")
    normalized_title = title.strip()
    if not normalized_title:
        raise ValueError("title must not be empty")
    task = {"title": normalized_title, "completed": False}`
- **Test result:** PASS (exit 0) — `python -m unittest discover -s tests -v`

### Change 2: empty-list percentage guard

- **File/location:** `src/task_manager.py:21`
- **Before:** `completed = sum(task["completed"] for task in tasks)`
- **After:** `if not tasks:
        return 0.0
    completed = sum(task["completed"] for task in tasks)`
- **Test result:** PASS (exit 0) — `python -m unittest discover -s tests -v`

### Change 3: HTML escaping

- **File/location:** `src/task_manager.py:29`
- **Before:** `return f'<li class="{status}">{task["title"]}</li>'`
- **After:** `safe_title = escape(str(task["title"]), quote=True)
return f'<li class="{status}">{safe_title}</li>'`
- **Test result:** PASS (exit 0) — `python -m unittest discover -s tests -v`

## Overall Status

**PASS.** All three planned changes were applied in order, and the smoke test passed after every change.

## Manual Verification

1. Run `python -m src.app` from `homework-4/`.
2. Confirm completion is `50.0%`.
3. Confirm the script-like title is printed as escaped text (`&lt;script&gt;`) rather than executable markup.
4. Run `python -m unittest discover -s tests -v`.

## References

- `implementation-plan.md`
- `research/verified-research.md`
- `src/task_manager.py`
