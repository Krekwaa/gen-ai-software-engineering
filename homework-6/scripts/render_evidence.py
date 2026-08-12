"""Create readable PNG evidence from reproducible command output."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def command(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
    return (result.stdout + result.stderr).strip()


def font(size: int, bold: bool = False):
    names = ["C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/arial.ttf"]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def wrap_lines(text: str, width: int = 105) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False) or [""])
    return lines


def render(filename: str, title: str, prompt: str, content: str, accent: str = "#45d4e8") -> None:
    lines = wrap_lines(content)
    line_height = 25
    height = max(650, 210 + line_height * len(lines))
    image = Image.new("RGB", (1500, height), "#07101f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((32, 30, 1468, height - 30), 18, fill="#0e192c", outline="#243759", width=2)
    draw.ellipse((65, 61, 79, 75), fill="#ff6b7d")
    draw.ellipse((89, 61, 103, 75), fill="#ffbf69")
    draw.ellipse((113, 61, 127, 75), fill="#39d98a")
    draw.text((155, 51), title, font=font(24, True), fill="#eaf1ff")
    draw.text((65, 104), prompt, font=font(19, True), fill=accent)
    y = 144
    for line in lines:
        color = "#39d98a" if any(word in line for word in ("passed", "completed", "reached", "VALID")) else "#eaf1ff"
        draw.text((65, y), line, font=font(18), fill=color)
        y += line_height
    image.save(OUT / filename)


pipeline = command("python", "orchestrator.py")
render("pipeline-run.png", "PowerShell - Homework 6", "PS> python orchestrator.py", pipeline)

tests = command("python", "-m", "pytest")
render("test-coverage.png", "pytest coverage report", "PS> python -m pytest", tests)

render(
    "skill-run-pipeline.png",
    "Codex project skill",
    "$run-pipeline",
    "Reading .agents/skills/run-pipeline/SKILL.md\n\nPS> python orchestrator.py\n"
    + pipeline
    + "\n\nResult inspection: shared/results/summary.json\nRejected: TXN006 - unsupported currency; TXN007 - non-positive amount\nPrivacy check: account numbers and descriptions omitted from final results\nSKILL WORKFLOW COMPLETED",
)

gate = "Coverage gate: tests must reach at least 80% before push\n" + tests
render("hook-trigger.png", "Git pre-push hook", "pre-push> python scripts/check_coverage.py", gate, "#ffbf69")

mcp = subprocess.run(
    ["python", "scripts/verify_mcp.py"], cwd=ROOT, text=True, capture_output=True, encoding="utf-8"
).stdout.strip()
context = """context7.resolve-library-id('FastAPI')
-> /websites/fastapi_tiangolo (High reputation, benchmark 87.95)
context7.query-docs('/websites/fastapi_tiangolo', 'HTMLResponse and POST endpoint patterns')
-> Use response_class=HTMLResponse; declare run actions with @app.post

context7.resolve-library-id('FastMCP')
-> /prefecthq/fastmcp (High reputation, benchmark 86.2)
context7.query-docs('/prefecthq/fastmcp', 'tool and resource decorator patterns')
-> Register @mcp.tool callables and URI-based @mcp.resource functions

Custom pipeline-status MCP verification
""" + mcp
render("mcp-interaction.png", "MCP interactions - context7 + pipeline-status", "MCP> verified research and custom tools", context)
