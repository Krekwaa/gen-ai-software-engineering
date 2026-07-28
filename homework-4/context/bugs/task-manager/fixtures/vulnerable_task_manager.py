"""Small task manager containing the deliberately seeded homework defects."""


def add_task(tasks, title):
    """Return a new task list containing title."""
    task = {"title": title, "completed": False}
    return [*tasks, task]


def completion_percentage(tasks):
    """Return the percentage of completed tasks."""
    completed = sum(task["completed"] for task in tasks)
    return round(completed / len(tasks) * 100, 2)


def render_task_html(task):
    """Render one task for the tiny HTML view."""
    status = "done" if task["completed"] else "open"
    return f'<li class="{status}">{task["title"]}</li>'
