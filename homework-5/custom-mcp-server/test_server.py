"""Unit and in-memory MCP protocol tests for the custom server."""

import unittest

from fastmcp import Client

from server import limited_words, mcp


class LimitedWordsTests(unittest.TestCase):
    def test_default_returns_exactly_thirty_words(self):
        self.assertEqual(len(limited_words().split()), 30)

    def test_requested_count_is_exact(self):
        self.assertEqual(len(limited_words(7).split()), 7)

    def test_rejects_zero(self):
        with self.assertRaises(ValueError):
            limited_words(0)

    def test_rejects_more_words_than_source_contains(self):
        with self.assertRaises(ValueError):
            limited_words(10_000)


class MCPProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_read_tool_returns_requested_words(self):
        async with Client(mcp) as client:
            result = await client.call_tool("read", {"word_count": 12})
            self.assertEqual(len(result.data.split()), 12)

    async def test_resource_default_and_parameter_are_available(self):
        async with Client(mcp) as client:
            default_content = await client.read_resource("lorem://ipsum")
            seven_word_content = await client.read_resource(
                "lorem://ipsum?word_count=7"
            )
            self.assertEqual(len(default_content[0].text.split()), 30)
            self.assertEqual(len(seven_word_content[0].text.split()), 7)


if __name__ == "__main__":
    unittest.main()
