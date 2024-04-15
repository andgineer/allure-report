import os
import pathlib
import shutil
import tempfile
from unittest.mock import patch

import pytest


def _get_repo_root_dir() -> str:
    """
    :return: path to the project folder.
    `tests/` should be in the same folder and this file should be in the root of `tests/`.
    """
    return str(pathlib.Path(__file__).parent.parent)


ROOT_DIR = _get_repo_root_dir()
RESOURCES = pathlib.Path(f"{ROOT_DIR}/tests/resources")


@pytest.fixture
def expected_index_file():
    with open(RESOURCES / "index.html", "r") as f:
        yield f


@pytest.fixture
def expected_executor_file():
    with open(RESOURCES / "executor.json", "r") as f:
        yield f


@pytest.fixture(scope="module")
def docker_compose_file():
    return RESOURCES


@pytest.fixture
def env():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        # Copy all contents of RESOURCES to the temporary directory
        shutil.copytree(RESOURCES, temp_path / 'resources', dirs_exist_ok=True)

        # Setup the environment variables to use paths in the temporary directory
        env_vars = {
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_REPOSITORY_OWNER": "owner",
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_RUN_NUMBER": "1",
            "GITHUB_RUN_ID": "1",
            "GITHUB_WORKFLOW": "CI/CD",
            "GITHUB_OUTPUT": str(temp_path / 'github/workflow/output'),
            "GITHUB_STEP_SUMMARY": str(temp_path / 'github/workflow/summary'),
            "INPUT_ALLURE-RESULTS": str(temp_path / 'resources/allure-results'),
            "INPUT_WEBSITE-SOURCE": str(temp_path / 'resources/website-source'),
            "INPUT_REPORTS-SITE-PATH": "builds/tests",
            "INPUT_REPORTS-SITE": str(temp_path / 'resources/temp/reports-site'),
            "INPUT_WEBSITE-URL": "",
            "INPUT_MAX-REPORTS": "20",
            "INPUT_CI-NAME": "GitHub Action: CI",
            "INPUT_REPORT-NAME": "Allure Report",
        }
        github_output_path = pathlib.Path(env_vars["GITHUB_OUTPUT"])
        # create github workflow folder for tests
        github_output_path.parent.mkdir(parents=True, exist_ok=True)

        with patch.dict(os.environ, env_vars):
            yield
