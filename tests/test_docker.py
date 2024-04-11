import os
import pytest
import tempfile
from testcontainers.compose import DockerCompose

SERVICE_NAME = "allure"


@pytest.fixture(scope="module")
def compose(docker_compose_file):
    with DockerCompose(docker_compose_file) as compose:
        yield compose


@pytest.fixture(scope="module")
def container(compose):
    return compose.get_container(SERVICE_NAME)


@pytest.fixture(scope="module")
def allure_results_dir():
    allure_results_dir = tempfile.mkdtemp()
    yield allure_results_dir
    os.rmdir(allure_results_dir)


@pytest.fixture(scope="module")
def allure_report_dir(compose):
    return compose.get_service_host(SERVICE_NAME)


def test_action_creates_allure_report(compose, allure_results_dir, allure_report_dir):
    compose.start()

    assert os.path.exists(allure_report_dir), "allure-report directory not created"

    compose.stop()

