$ErrorActionPreference = "Stop"

uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest --cov=suj --cov-branch
uv run okf-parser check .
uv run pip-audit
