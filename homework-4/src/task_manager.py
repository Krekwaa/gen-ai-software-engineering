"""Core behavior for the homework task-manager mini application."""

from html import escape


def add_task(tasks, title):
    """Return a new task list containing title."""
    if not isinstance(title, str):
        raise TypeError("title must be a string")
    normalized_title = title.strip()
    if not normalized_title:
        raise ValueError("title must not be empty")
    task = {"title": normalized_title, "completed": False}
    return [*tasks, task]


def completion_percentage(tasks):
    """Return the percentage of completed tasks."""
    if not tasks:
        return 0.0
    completed = sum(task["completed"] for task in tasks)
    return round(completed / len(tasks) * 100, 2)


def render_task_html(task):
    """Render one task for the tiny HTML view."""
    status = "done" if task["completed"] else "open"
    safe_title = escape(str(task["title"]), quote=True)
    return f'<li class="{status}">{safe_title}</li>'
