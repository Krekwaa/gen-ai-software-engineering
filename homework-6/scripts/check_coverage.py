"""Run the mandatory coverage gate."""

import subprocess
import sys
import os
from pathlib import Path

project = Path(__file__).resolve().parents[1]
base_temp = project / ".tmp" / f"pytest-hook-{os.getpid()}"
raise SystemExit(
    subprocess.call(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            f"--basetemp={base_temp}",
        ],
        cwd=project,
    )
)
