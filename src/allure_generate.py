"""Generate Allure report Github Action."""

import os
import shutil
import subprocess
import sys
import traceback
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

        self.website = self.get_input_path("website")
        self.reports_site_path = self.input["reports-site-path"]
        self.prev_reports = (
            self.website / self.reports_site_path
            if self.reports_site_path
            else self.website
        )
        self.prev_reports.mkdir(parents=True, exist_ok=True)
        if self.input["reports-site"]:
            self.reports_site = self.get_input_path("reports-site")
        else:
            self.reports_site = self.prev_reports
        self.reports_site.mkdir(parents=True, exist_ok=True)

        self.website_url = self.input["website-url"]
        if not self.website_url:
            repository_name = self.github_repository.split("/")[-1]  # owner/repo
            self.website_url = (
                f"https://{self.github_repository_owner}.github.io/{repository_name}"
            )
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

    def main(self) -> None:
        """Generate Allure report."""
        # 1st copy old reports to result directory to make it safe to republish
        if self.prev_reports != self.reports_site:
            shutil.copytree(self.prev_reports, self.reports_site, dirs_exist_ok=True)
        if not any(self.allure_results.iterdir()):
            raise ValueError(f"No Allure results found in `{self.allure_results}`.")
        self.generate_allure_report()
        self.cleanup_reports()
        self.create_index_html()
        self.output["REPORT_URL"] = self.last_report_folder_url + "index.html"
        self.output["REPORTS_ROOT_URL"] = self.root_url
        self.output["REPORTS_SITE_PATH"] = self.reports_site_path
        self.output["REPORTS_SITE"] = str(self.reports_site)

    def run(self) -> None:
        """Run main method."""
        try:
            self.main()
        except Exception:  # pylint: disable=broad-except
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

    def cleanup_reports(self) -> None:
        """Cleanup old reports if max history reports is set.

        In site report folder each report is stored in a separate sub folder.
        """
        reports_folders = [
            f
            for f in self.reports_site.glob("*")
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
    def root_url(self) -> str:
        """Get URL to the last report."""
        if self.reports_site_path:
            return "/".join([self.website_url, self.reports_site_path])
        return self.website_url  # type: ignore

    @cached_property
    def last_report_folder_url(self) -> str:
        """Get URL to the last report."""
        return "/".join([self.root_url, self.github_run_number]) + "/"

    def create_index_html(self) -> None:
        """Create index.html in the report folder root with redirect to the last report."""
        template = self.environment.get_template("index.html")
        rendered_template = template.render(
            url=self.last_report_folder_url + "index.html"
        )
        (self.reports_site / "index.html").write_text(rendered_template)

    def generate_allure_report(self) -> None:
        """Prepare params and Call allure generate."""
        template = self.environment.get_template("executor.json")
        # https://allurereport.org/docs/how-it-works-executor-file/
        rendered_template = template.render(
            report_url=self.last_report_folder_url,
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
        (self.prev_reports / "last-history").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            self.prev_reports / "last-history",
            self.allure_results / "history",
            dirs_exist_ok=True,
        )

        print(
            f"Generating report from {self.allure_results} to {self.reports_site} ..."
        )
        subprocess.run(
            [
                "allure",
                "generate",
                "--clean",
                str(self.allure_results),
                "-o",
                str(self.reports_site / self.github_run_number),
            ],
            check=True,
        )

        shutil.copytree(
            self.reports_site / self.github_run_number / "history",
            self.reports_site / "last-history",
            dirs_exist_ok=True,
        )


if __name__ == "__main__":  # pragma: no cover
    generator = AllureGenerator()
    generator.run()
