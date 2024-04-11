import os
import pathlib
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
    with patch.dict(os.environ, {
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_REPOSITORY_OWNER": "owner",
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_RUN_NUMBER": "1",
        "GITHUB_RUN_ID": "1",
        "INPUT_SITE_PATH": "site-path",
        "INPUT_ALLURE_HISTORY": "allure-history",
        "INPUT_ALLURE_RESULTS": "allure-results",
        "INPUT_ALLURE_REPORT": "allure-report",
        "INPUT_SITE_SOURCE": "site-source",
        "INPUT_SITE_URL": "",
        "INPUT_NUMBER_REPORTS_TO_KEEP": "20",
        "INPUT_CI_NAME": "GitHub Action: CI",
        "INPUT_REPORT_NAME": "Allure Report",
    }):
        yield
