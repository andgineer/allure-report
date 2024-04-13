import os
import shutil

import pytest
import tempfile
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
    folder = RESOURCES / "temp" / "allure-report"
    yield folder
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)


@pytest.mark.docker
def test_allure_generate_docker(compose, report_dir):
    compose.start()

    assert report_dir.exists(), "allure directory not created"

    compose.stop()

