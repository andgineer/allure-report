import sys

from invoke import task, Context, Collection
import subprocess

ALLOWED_VERSION_TYPES = ["release", "bug", "feature"]


@task
def version(c: Context):
    """Show the current version."""
    with open("src/__about__.py", "r") as f:
        version_line = f.readline()
        version_num = version_line.split('"')[1]
        print(version_num)
        return version_num


def ver_task_factory(version_type: str):
    @task
    def ver(c: Context):
        """Bump the version."""
        c.run(f"./scripts/verup_action.sh {version_type}")

    return ver


@task
def compile_requirements(c: Context):
    "Convert requirements.in to requirements.txt and requirements.dev.txt."
    start_time = subprocess.check_output(["date", "+%s"]).decode().strip()
    c.run("uv pip compile requirements.in --output-file=requirements.txt")
    reqs_time = subprocess.check_output(["date", "+%s"]).decode().strip()
    c.run("uv pip compile requirements.dev.in --output-file=requirements.dev.txt")
    end_time = subprocess.check_output(["date", "+%s"]).decode().strip()
    print(f"Req's compilation time: {int(reqs_time) - int(start_time)} seconds")
    print(f"Req's dev compilation time: {int(end_time) - int(reqs_time)} seconds")
    print(f"Total execution time: {int(end_time) - int(start_time)} seconds")


@task(pre=[compile_requirements])
def reqs(c: Context):
    """Upgrade requirements including pre-commit."""
    c.run("pip install -r requirements.dev.txt")


@task
def uv(c: Context):
    """Install or upgrade uv."""
    c.run("curl -LsSf https://astral.sh/uv/install.sh | sh")


@task
def pre(c):
    """Run pre-commit checks"""
    c.run("pre-commit run --verbose --all-files")


@task
def run(c):
    """Run the action locally."""
    c.run("docker-compose -f tests/resources/docker-compose.yml up  --build")


@task
def logs(c):
    """Show the logs of the action."""
    c.run("docker-compose -f tests/resources/docker-compose.yml logs")


@task
def container(c):
    """Enter the container."""
    c.run(
        "docker-compose -f tests/resources/docker-compose.yml run -it --entrypoint="
        " --build upn"
    )


namespace = Collection.from_module(sys.modules[__name__])
for name in ALLOWED_VERSION_TYPES:
    namespace.add_task(ver_task_factory(name), name=f"ver-{name}")
