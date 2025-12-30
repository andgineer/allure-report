# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a GitHub Action for generating Allure test reports from Allure test results. The action creates visually stunning reports with test history and publishes them to GitHub Pages or any static web server.

## Architecture

- **Main Entry Point**: `src/allure_generate.py` - The core logic for generating Allure reports
- **Docker-based Action**: Uses `Dockerfile` to package the action for GitHub Actions
- **Templating**: Uses Jinja2 templates in `src/templates/` for generating executor.json and index.html
- **Build System**: Uses `invoke` tasks defined in `tasks.py` for development workflows
- **Dependencies**: Python-based with requirements managed via uv pip-tools

## Common Development Commands

### Environment Setup
```bash
# Set up or activate development environment
source ./activate.sh
```

**IMPORTANT**: Always activate the virtual environment before running any commands. Use `source ./activate.sh` before each command.

### Build and Test
```bash
# Install dependencies
source ./activate.sh && pip install -r requirements.dev.txt

# Run tests
source ./activate.sh && python -m pytest tests/

# Run pre-commit checks (formatting, linting)
source ./activate.sh && inv pre
```

**IMPORTANT**: Always use `inv pre` or `pre-commit run --all-files` for code quality checks. Never run ruff or mypy directly.

# Run tests with Docker (requires Docker)
source ./activate.sh && inv run
source ./activate.sh && inv logs

# Enter container for debugging
source ./activate.sh && inv container
```

### Dependency Management
```bash
# Update requirements files
inv reqs

# Install/upgrade uv
inv uv
```

### Docker Operations
```bash
# Build Docker image
inv build

# Remove containers
inv rm
```

### Version Management
```bash
# Show current version
inv version

# Bump version (release, bug, feature)
inv ver-release
inv ver-bug
inv ver-feature
```

## Code Style

- **Linting**: Uses `ruff` with line length of 99 characters
- **Pre-commit**: Configured for automatic formatting and linting
- **Type Hints**: Extensive use of type annotations throughout the codebase

## Testing

- **Framework**: pytest with `--doctest-modules`
- **Docker Tests**: Marked with `@pytest.mark.docker` and require Docker via testcontainers
- **Test Structure**:
  - `test_allure_report.py` - Unit tests
  - `test_e2e_local.py` - End-to-end tests (local)
  - `test_e2e_docker.py` - End-to-end tests (Docker)

## Key Components

### AllureGenerator Class
The main class (`src/allure_generate.py:60`) that handles:
- Input validation and processing
- Report generation using allure CLI
- History management and cleanup
- GitHub Pages integration

### Action Inputs/Outputs
- Defined in `action.yml`
- Typed classes: `AllureGeneratorInputs` and `AllureGeneratorOutputs`
- Key inputs: `allure-results`, `website`, `reports-site-path`, `max-reports`

### Templates
- `src/templates/executor.json` - Allure executor configuration
- `src/templates/index.html` - Auto-redirect page template
