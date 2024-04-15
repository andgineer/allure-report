"""Generate Allure report Github Action."""

import os
import shutil
import subprocess
from functools import cached_property
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .inputs_outputs import InputProxy, OutputProxy  # pylint: disable=relative-beyond-top-level
from .__about__ import __version__  # pylint: disable=relative-beyond-top-level


class AllureGenerator:  # pylint: disable=too-many-instance-attributes
    """Generate Allure report from Allure test results to publish it to GitHub Pages.

    Report is generated from Allure results folder specified in action input `allure-results`.
    And saved to the subfolder in the folder specified in input `allure-report`.
    Creates index.html in the root of the report folder with redirect to the last report.
    """

    def __init__(self) -> None:
        print(f"Generate Allure Report action v.{__version__}")

        self.github_repository = os.environ["GITHUB_REPOSITORY"]
        self.github_repository_owner = os.environ["GITHUB_REPOSITORY_OWNER"]
        self.github_server_url = os.environ["GITHUB_SERVER_URL"]
        self.github_run_number = os.environ["GITHUB_RUN_NUMBER"]
        self.github_run_id = os.environ["GITHUB_RUN_ID"]

        # Action inputs
        self.allure_results = self.get_input_path("allure-results")
        self.website_source = self.get_input_path("website-source")
        self.report_path = self.input["report-path"]
        self.allure_report = self.get_input_path("allure-report")
        self.website_url = self.input["website-url"]
        self.report_name = self.input["report-name"]
        if self.input["ci-name"]:
            self.ci_name = self.input["ci-name"]
        else:
            self.ci_name = f"GitHub Action: {os.getenv('GITHUB_WORKFLOW')}"
        self.max_history_reports = (
            int(self.input["max-reports"]) if self.input["max-reports"] else 0
        )
        if self.max_history_reports < 0:
            raise ValueError("max-reports cannot be negative.")

        base_dir = Path(__file__).resolve().parent
        templates_dir = base_dir / "templates"
        self.environment = Environment(loader=FileSystemLoader(str(templates_dir)))

        shutil.rmtree(self.allure_report, ignore_errors=True)
        self.allure_report.mkdir(parents=True, exist_ok=True)
        self.prev_report = (
            self.website_source / self.report_path
            if self.report_path
            else self.website_source
        )
        self.prev_report.mkdir(parents=True, exist_ok=True)
        if not self.website_url:
            repository_name = self.github_repository.split("/")[-1]  # owner/repo
            self.website_url = (
                f"https://{self.github_repository_owner}.github.io/{repository_name}"
            )

    @property
    def output(self) -> OutputProxy:
        """Get Action Output."""
        return OutputProxy()

    @property
    def input(self) -> InputProxy:
        """Get Action Input."""
        return InputProxy()

    def get_input_path(self, name: str) -> Path:
        """Get Action Input value as Path."""
        path_str = self.input[name]
        if not path_str:
            raise ValueError(f"Parameter `{name}` cannot be empty.")
        return Path(path_str)

    def run(self) -> None:
        """Generate Allure report."""
        # 1st copy old reports to result directory to make it safe to republish
        shutil.copytree(self.prev_report, self.allure_report, dirs_exist_ok=True)
        if not any(self.allure_results.iterdir()):
            print("No Allure results found, skipping report generation.")
            return
        self.cleanup_reports()
        self.generate_allure_report()
        self.create_index_html()
        self.output["REPORT_URL"] = self.last_report_url

    def cleanup_reports(self) -> None:
        """Cleanup old reports if max history reports is set.

        In site report folder each report is stored in a separate sub folder.
        """
        reports_folders = [
            f
            for f in self.allure_report.glob("*")
            if f.is_dir() and f.name != "last-history"
        ]
        print(
            f"Found {len(reports_folders)} report(s) in history, "
            f"keeping {self.max_history_reports}"
        )
        if (
            self.max_history_reports
            and len(reports_folders)
            > self.max_history_reports  # already excluding index.html and CNAME
        ):
            reports_folders.sort(key=lambda x: x.stat().st_mtime)
            excess_count = len(reports_folders) - self.max_history_reports

            # Remove the oldest reports which are the first 'excess_count' elements
            for report in reports_folders[:excess_count]:
                print(f"Removing {report.name} ...")
                report.unlink()

    @cached_property
    def last_report_url(self) -> str:
        """Get URL to the last report."""
        url_parts = [self.website_url, self.github_run_number, "index.html"]
        if self.report_path:
            url_parts.insert(1, self.report_path)
        return "/".join(url_parts)

    def create_index_html(self) -> None:
        """Create index.html in the report folder root with redirect to the last report."""
        template = self.environment.get_template("index.html")
        rendered_template = template.render(url=self.last_report_url)
        (self.allure_report / "index.html").write_text(rendered_template)

    def generate_allure_report(self) -> None:
        """Prepare params and Call allure generate."""
        template = self.environment.get_template("executor.json")
        # https://allurereport.org/docs/how-it-works-executor-file/
        rendered_template = template.render(
            url=self.last_report_url,
            report_name=self.report_name,
            ci_name=self.ci_name,
            github_run_number=self.github_run_number,
            github_server_url=self.github_server_url,
            github_run_id=self.github_run_id,
            github_repository=self.github_repository,
        )
        (self.allure_results / "executor.json").write_text(rendered_template)

        # https://allurereport.org/docs/how-it-works-history-files/
        # Copy last report history to the allure results so that it is included in the new report
        (self.prev_report / "last-history").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            self.prev_report / "last-history",
            self.allure_results / "history",
            dirs_exist_ok=True,
        )

        print(
            f"Generating report from {self.allure_results} to {self.allure_report} ..."
        )
        subprocess.run(
            [
                "allure",
                "generate",
                "--clean",
                str(self.allure_results),
                "-o",
                str(self.allure_report / self.github_run_number),
            ],
            check=True,
        )

        shutil.copytree(
            self.allure_report / self.github_run_number / "history",
            self.allure_report / "last-history",
            dirs_exist_ok=True,
        )


if __name__ == "__main__":  # pragma: no cover
    generator = AllureGenerator()
    generator.run()
