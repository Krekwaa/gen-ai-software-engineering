"""Agent-generated tests for behavior changed by the implementation plan."""

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
