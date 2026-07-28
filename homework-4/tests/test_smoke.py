"""Stable smoke tests run by the Bug Fixer after each individual change."""

import unittest

from src.task_manager import add_task


class TaskManagerSmokeTests(unittest.TestCase):
    def test_add_task_returns_a_new_list(self):
        original = []
        result = add_task(original, "Write report")
        self.assertEqual(original, [])
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]["completed"])


if __name__ == "__main__":
    unittest.main()
