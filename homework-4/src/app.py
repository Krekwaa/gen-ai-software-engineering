"""Runnable command-line demonstration of the fixed task manager."""

from src.task_manager import add_task, completion_percentage, render_task_html


def main():
    tasks = []
    tasks = add_task(tasks, "  Review agent reports  ")
    tasks = add_task(tasks, "<script>alert('demo')</script>")
    tasks[0]["completed"] = True

    print("Task Manager Demo")
    print(f"Completion: {completion_percentage(tasks)}%")
    print("Safe HTML:")
    for task in tasks:
        print(f"  {render_task_html(task)}")


if __name__ == "__main__":
    main()
