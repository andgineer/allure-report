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
            "INPUT_ALLURE-RESULTS": str(temp_path / 'resources/allure-results'),
            "INPUT_WEBSITE-SOURCE": str(temp_path / 'resources/website-source'),
            "INPUT_REPORT-PATH": "report-path",
            "INPUT_ALLURE-REPORT": str(temp_path / 'resources/temp/allure-report'),
            "INPUT_WEBSITE-URL": "",
            "INPUT_MAX-REPORTS": "20",
            "INPUT_CI-NAME": "GitHub Action: CI",
            "INPUT_REPORT-NAME": "Allure Report",
        }

        with patch.dict(os.environ, env_vars):
            yield
