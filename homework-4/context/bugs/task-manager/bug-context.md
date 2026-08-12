# Task Manager Seeded Bug Context

## Scope

The sample application is a dependency-free Python task manager. Its
deliberately vulnerable before-state is preserved in
`fixtures/vulnerable_task_manager.py`; the pipeline copies that file into
`src/task_manager.py` at the beginning of a run and leaves the corrected
after-state in `src/`.

## Seeded issues

1. **Input-normalization bug**: `add_task` accepts blank titles and preserves
   accidental surrounding whitespace.
2. **Empty-list bug**: `completion_percentage` divides by zero when no tasks
   exist.
3. **Security issue (XSS)**: `render_task_html` interpolates an untrusted task
   title into HTML without escaping it.

## Expected outcome

The pipeline validates and trims titles, returns `0.0` for an empty task list,
HTML-escapes task titles, generates regression tests, and leaves all tests
passing.
