"""Install the repository-local pre-push coverage hook."""

from pathlib import Path

project = Path(__file__).resolve().parents[1]
hook = project / ".githooks" / "pre-push"
hook.chmod(0o755)
print("Run from repository root: git config core.hooksPath homework-6/.githooks")

