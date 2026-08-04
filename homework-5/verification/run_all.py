"""Run every non-OAuth Homework 5 verification in one command."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CUSTOM = ROOT / "custom-mcp-server"


def run(label: str, command: list[str], cwd: Path = ROOT) -> None:
    print(f"\n=== {label} ===", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    run(
        "Configuration",
        [sys.executable, str(ROOT / "verification" / "verify_configuration.py")],
    )
    run(
        "Custom server tests",
        [sys.executable, "-m", "unittest", "-v", "test_server.py"],
        CUSTOM,
    )
    run(
        "Custom server stdio",
        [sys.executable, str(ROOT / "verification" / "verify_custom_stdio.py")],
    )
    run(
        "Filesystem MCP stdio",
        [sys.executable, str(ROOT / "verification" / "verify_filesystem_mcp.py")],
    )
    print("\nALL NON-OAUTH CHECKS: PASS")


if __name__ == "__main__":
    main()
