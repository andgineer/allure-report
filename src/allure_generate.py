"""Generate Allure report Github Action."""

import os
import shutil
import subprocess
from functools import cached_property
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .inputs_outputs import ActionInputs  # pylint: disable=relative-beyond-top-level
from .action_base import ActionBase  # pylint: disable=relative-beyond-top-level
from .__about__ import __version__  # pylint: disable=relative-beyond-top-level


class AllureGeneratorInputs(ActionInputs):  # type: ignore  # pylint: disable=too-few-public-methods
    """Action inputs."""

    allure_results: Path
    """Allure results directory."""

    website: Path
    """Website folder."""

    reports_site_path: str
    """Path to the reports site folder."""

    reports_site: Path
    """Reports site folder."""

    website_url: str
    """Website URL to replace github-pages.io URL with."""

    max_reports: str
    """Maximum history reports to keep."""

    ci_name: str
    """CI name to use in the report."""

    report_name: str
    """Report name to use in the report."""


class AllureGenerator(ActionBase):  # type: ignore  # pylint: disable=too-many-instance-attributes
    """Generate Allure report from Allure test results to publish it to GitHub Pages."""

    def __init__(self) -> None:
        super().__init__(inputs=AllureGeneratorInputs())

        print(f"Generate Allure Report action v.{__version__}")

        if self.inputs.allure_results is None:
            raise ValueError("Parameter `allure-results` cannot be empty.")
        if self.inputs.website is None:
            raise ValueError("Parameter `website` cannot be empty.")

        self.prev_reports = (
            self.inputs.website / self.inputs.reports_site_path
            if self.inputs.reports_site_path
            else self.inputs.website
        )
        self.prev_reports.mkdir(parents=True, exist_ok=True)

        self.reports_site = self.inputs.reports_site or self.prev_reports
        self.reports_site.mkdir(parents=True, exist_ok=True)

        self.ci_name = self.inputs.ci_name or f"GitHub Action: {os.getenv('GITHUB_WORKFLOW')}"
        self.max_history_reports = int(self.inputs.max_reports or 0)
        if self.max_history_reports < 0:
            raise ValueError("max-reports cannot be negative.")

        base_dir = Path(__file__).resolve().parent
        templates_dir = base_dir / "templates"
        self.environment = Environment(loader=FileSystemLoader(str(templates_dir)))

    def main(self) -> None:
        """Generate Allure report."""
        # 1st copy old reports to result directory to make it safe to republish
        if self.prev_reports != self.reports_site:
            shutil.copytree(self.prev_reports, self.reports_site, dirs_exist_ok=True)
        if not any(self.inputs.allure_results.iterdir()):
            raise ValueError(f"No Allure results found in `{self.inputs.allure_results}`.")
        self.generate_allure_report()
        self.cleanup_reports()
        self.create_index_html()
        self.outputs["REPORT_URL"] = f"{self.last_report_folder_url}index.html"
        self.outputs["REPORTS_ROOT_URL"] = self.root_url
        self.outputs["REPORTS_SITE_PATH"] = self.inputs.reports_site_path
        self.outputs["REPORTS_SITE"] = str(self.reports_site)
        print(
            self.vars.github_step_summary.write_text(
                "# Allure report generated.\nHave a nice day!"
            )
        )

    def cleanup_reports(self) -> None:
        """Cleanup old reports if max history reports is set.

        In site report folder each report is stored in a separate sub folder.
        """
        reports_folders = [
            f for f in self.reports_site.glob("*") if f.is_dir() and f.name != "last-history"
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
        """Get URL to the root of reports."""
        if not self.inputs.website_url:
            repository_name = self.vars.github_repository.split("/")[-1]  # owner/repo
            url = f"https://{self.vars.github_repository_owner}.github.io/{repository_name}"
        else:
            url = self.inputs.website_url
        if self.inputs.reports_site_path:
            return "/".join([url, self.inputs.reports_site_path])
        return url

    @cached_property
    def last_report_folder_url(self) -> str:
        """Get URL to the last report."""
        return "/".join([self.root_url, self.vars.github_run_number]) + "/"

    def create_index_html(self) -> None:
        """Create index.html in the report folder root with redirect to the last report."""
        template = self.environment.get_template("index.html")
        rendered_template = template.render(url=f"{self.last_report_folder_url}index.html")
        (self.reports_site / "index.html").write_text(rendered_template)

    def generate_allure_report(self) -> None:
        """Prepare params and Call allure generate."""
        template = self.environment.get_template("executor.json")
        # https://allurereport.org/docs/how-it-works-executor-file/
        rendered_template = template.render(
            report_url=self.last_report_folder_url,
            report_name=self.inputs.report_name,
            ci_name=self.ci_name,
            github_run_number=self.vars.github_run_number,
            github_server_url=self.vars.github_server_url,
            github_run_id=self.vars.github_run_id,
            github_repository=self.vars.github_repository,
        )
        (self.inputs.allure_results / "executor.json").write_text(rendered_template)

        # https://allurereport.org/docs/how-it-works-history-files/
        # Copy last report history to the allure results so that it is included in the new report
        (self.prev_reports / "last-history").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            self.prev_reports / "last-history",
            self.inputs.allure_results / "history",
            dirs_exist_ok=True,
        )

        print(f"Generating report from {self.inputs.allure_results} to {self.reports_site} ...")
        subprocess.run(
            [
                "allure",
                "generate",
                "--clean",
                str(self.inputs.allure_results),
                "-o",
                str(self.reports_site / self.vars.github_run_number),
            ],
            check=True,
        )

        shutil.copytree(
            self.reports_site / self.vars.github_run_number / "history",
            self.reports_site / "last-history",
            dirs_exist_ok=True,
        )


if __name__ == "__main__":  # pragma: no cover
    AllureGenerator().run()
