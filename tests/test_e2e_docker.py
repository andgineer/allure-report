"""Dockerized e2e tests.

With real allure generate call.
"""

import os
import shutil
import docker
import pytest

from tests.conftest import RESOURCES


@pytest.fixture
def report_dir():
    # cleanup folder created by container
    # the folder for test defined in tests/resources/.env#INPUT_ALLURE_REPORT
    yield RESOURCES / "temp" / "reports-site"
    shutil.rmtree(RESOURCES / "temp", ignore_errors=True)
    (RESOURCES / "allure-results" / "executor.json").unlink(missing_ok=True)
    shutil.rmtree(RESOURCES / "allure-results" / "history", ignore_errors=True)


@pytest.mark.docker
def test_allure_generate_docker(report_dir):
    client = docker.from_env()

    # Build the image
    pull = os.getenv("ALLURE_IMAGE_PULL", "").lower() in ("1", "true", "yes")
    image, _ = client.images.build(path=".", tag="allure-test", pull=pull)

    # Set up volume bindings equivalent to docker-compose
    volumes = {
        str(RESOURCES / "allure-results"): {
            "bind": "/github/workspace/allure-results",
            "mode": "rw",
        },
        str(RESOURCES / "gh-pages-dir"): {"bind": "/github/workspace/gh-pages-dir", "mode": "rw"},
        str(RESOURCES / "temp/reports-site"): {
            "bind": "/github/workspace/reports-site",
            "mode": "rw",
        },
        str(RESOURCES / "temp/workflow"): {"bind": "/github/workflow", "mode": "rw"},
    }

    # Read environment variables from .env file
    with open(RESOURCES / ".env") as f:
        env_vars = dict(
            line.strip().split("=", 1)
            for line in f
            if line.strip() and not line.strip().startswith("#")
        )

    try:
        # Run the container
        container = client.containers.run(
            "allure-test",
            detach=True,
            volumes=volumes,
            environment=env_vars,
            working_dir="/github/workspace",
        )

        # Wait for container to finish and get logs
        result = container.wait()
        logs = container.logs().decode("utf-8")
        print(logs)

        if result["StatusCode"] != 0:
            raise Exception(f"Container exited with error: {logs}")

        # Verify the results
        assert report_dir.exists(), "allure directory not created"
        assert (report_dir / "2" / "history" / "history.json").exists()
        assert (report_dir / "2" / "index.html").exists()
        assert (report_dir / "22" / "history" / "history.json").exists()
        assert (report_dir / "last-history" / "history.json").exists()

    except Exception as e:
        print(f"Error: {e}")
        if "container" in locals():
            print(f"Container logs: {container.logs().decode('utf-8')}")
        raise

    finally:
        # Cleanup
        if "container" in locals():
            container.remove(force=True)
