"""Shared application configuration."""

APP_TITLE = "AI Coding IDE"
WINDOW_SIZE = "1600x900"
PYTHON_FILE_TYPES = (("Python files", "*.py"), ("All files", "*.*"))

IGNORED_DIRECTORIES = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "env",
    "node_modules",
    "venv",
}

