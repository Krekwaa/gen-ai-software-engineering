"""FastMCP server exposing word-limited content from lorem-ipsum.md."""

from pathlib import Path

from fastmcp import FastMCP


SOURCE_FILE = Path(__file__).with_name("lorem-ipsum.md")
mcp = FastMCP("Homework 5 Lorem Reader")


def limited_words(word_count: int = 30) -> str:
    """Return exactly ``word_count`` words from the local source document."""
    if isinstance(word_count, bool) or not isinstance(word_count, int):
        raise TypeError("word_count must be an integer")
    if word_count < 1:
        raise ValueError("word_count must be at least 1")

    words = SOURCE_FILE.read_text(encoding="utf-8").split()
    if word_count > len(words):
        raise ValueError(
            f"word_count must not exceed the {len(words)} words in lorem-ipsum.md"
        )
    return " ".join(words[:word_count])


@mcp.resource(
    "lorem://ipsum{?word_count}",
    name="LoremIpsumExcerpt",
    description="Read an exact number of words from lorem-ipsum.md (default 30).",
    mime_type="text/plain",
)
def lorem_resource(word_count: int = 30) -> str:
    """MCP resource template for the word-limited lorem ipsum excerpt."""
    return limited_words(word_count)


@mcp.tool(name="read")
def read_tool(word_count: int = 30) -> str:
    """Read exactly word_count words from the lorem ipsum resource."""
    return limited_words(word_count)


if __name__ == "__main__":
    mcp.run(transport="stdio")
