# Repository Guidelines

## Project Structure & Modules
- `src/`: action code. Entry point: `src/allure_generate.py`; templates in `src/templates/`.
- `tests/`: pytest suite (unit and e2e). Shared fixtures in `tests/conftest.py`.
- `tasks.py`: Invoke tasks for local run, Docker build, versioning.
- `action.yml`: GitHub Action metadata and inputs/outputs.
- `Dockerfile`: container image used by the action.
- `scripts/`: helper scripts (e.g., version bump).

## Build, Test, and Development Commands
- Setup venv: `. ./activate.sh` then `pre-commit install`.
- Run tests: `pytest tests/` or with coverage `pytest --cov`.
- Skip Docker-marked tests locally: `pytest -m "not docker"`.
- Run the action locally in Docker: `inv run`; view logs `inv logs`; open shell `inv container`.
- List available tasks: `inv --list`; build image: `inv build`.

## Coding Style & Naming Conventions
- Indentation 4 spaces; max line length 99 (`ruff.toml`, `.flake8`).
- Tools: Ruff, Flake8, Pylint, Mypy, Pre-commit. Run: `pre-commit run --all-files`.
- Typing: add/keep type hints where practical.
- Naming: modules/files `snake_case.py`; classes `PascalCase`; functions/vars `snake_case`; constants `UPPER_SNAKE`.

## Testing Guidelines
- Framework: Pytest (+ `pytest-cov`). Place tests in `tests/` as `test_*.py`.
- Markers: `docker` for Testcontainers-based e2e. Use selective runs as needed.
- Keep tests deterministic; prefer unit tests for logic in `allure_generate.py`; add e2e for Docker behavior.

## Commit & Pull Request Guidelines
- Commits: short, imperative subject (≤72 chars). Version bumps follow existing style, e.g., `Version v3.x`.
- Reference issues (`Fixes #123`) and keep logical changes atomic.
- PRs: clear description, rationale, and scope; link issues; include screenshots or a report URL when touching report generation/output.
- Requirements: passing CI, updated docs (`README.md`/`action.yml`) when inputs/outputs or behavior change.

## Security & Configuration Tips
- The action runs in Docker (Linux-only). Do not commit secrets; local env for tests lives in `tests/resources/.env`.
- Allure results are consumed from `allure-results/`; history is kept under the website path defined by inputs.
