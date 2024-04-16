"""Dockerized e2e tests.

With real allure generate call.
"""
import shutil

import pytest
from testcontainers.compose import DockerCompose

from tests.conftest import RESOURCES

SERVICE_NAME = "allure"


@pytest.fixture(scope="module")
def compose(docker_compose_file):
    with DockerCompose(docker_compose_file, build=True) as compose:
        yield compose


@pytest.fixture(scope="module")
def container(compose):
    return compose.get_container(SERVICE_NAME)


@pytest.fixture
def report_dir():
    # cleanup folder created by container
    # the folder for test defined in tests/resources/.env#INPUT_ALLURE_REPORT
    yield RESOURCES / "temp" / "reports-site"
    shutil.rmtree(RESOURCES / "temp", ignore_errors=True)
    (RESOURCES / "allure-results" / "executor.json").unlink(missing_ok=True)
    shutil.rmtree(RESOURCES / "allure-results" / "history", ignore_errors=True)


@pytest.mark.docker
def test_allure_generate_docker(compose, report_dir):
    compose.start()

    assert report_dir.exists(), "allure directory not created"

    compose.stop()
    assert (report_dir / "2" / "history" / "history.json").exists()
    assert (report_dir / "2" / "index.html").exists()
    assert (report_dir / "22" / "history" / "history.json").exists()
    assert (report_dir / "last-history" / "history.json").exists()
