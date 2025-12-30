"""Generate Allure report Github Action."""

import re
import shutil
import subprocess
from functools import cached_property
from pathlib import Path

from github_custom_actions import ActionBase, ActionInputs, ActionOutputs
from jinja2 import Environment, FileSystemLoader

from __about__ import __version__


class AllureGeneratorInputs(ActionInputs):  # type: ignore  # pylint: disable=too-few-public-methods
    """Action inputs."""

    # pylint: disable=abstract-method  # we want RO implementation that raises NotImplementedError on write

    allure_results: Path
    """Allure results directory."""

    website: Path
    """Website folder."""

    reports_site_path: str
    """Path to the reports site folder."""

    reports_site: Path
    """Reports site folder."""

    report_page: str
    """Allure report page to be opened by default."""

    website_url: str
    """Website URL to replace github-pages.io URL with."""

    max_reports: str
    """Maximum history reports to keep."""

    ci_name: str
    """CI name to use in the report."""

    report_name: str
    """Report name to use in the report."""

    summary: str
    """Summary of the action."""


class AllureGeneratorOutputs(ActionOutputs):  # type: ignore  # pylint: disable=too-few-public-methods
    """Action outputs."""

    report_url: str
    reports_root_url: str
    reports_site_path: str
    reports_site: Path


class AllureGenerator(ActionBase):  # type: ignore  # pylint: disable=too-many-instance-attributes
    """Generate Allure report from Allure test results to publish it to GitHub Pages."""

    inputs: AllureGeneratorInputs  # type: ignore[bad-override]
    outputs: AllureGeneratorOutputs  # type: ignore[bad-override]

    def __init__(self) -> None:
        super().__init__()

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
        self.outputs.report_url = f"{self.last_report_file_url}{self.report_page()}"
        self.outputs.reports_root_url = self.root_url
        self.outputs.reports_site_path = self.inputs.reports_site_path
        self.outputs.reports_site = self.reports_site
        self.summary += self.render(self.inputs.summary)
        print(f"Report URL: {self.outputs.report_url}")

    def cleanup_reports(self) -> None:
        """Cleanup old reports if max history reports is set.

        In site report folder each report is stored in a separate sub folder.
        """
        reports_folders = [
            f for f in self.reports_site.glob("*") if f.is_dir() and re.match(r"^\d+$", f.name)
        ]
        print(
            f"Found {len(reports_folders)} report(s) in history, "
            f"keeping {self.max_history_reports}",
        )
        if (
            self.max_history_reports
            and len(reports_folders)
            > self.max_history_reports  # already excluding index.html and CNAME
        ):
            reports_folders.sort(key=lambda x: int(x.name))
            excess_count = len(reports_folders) - self.max_history_reports

            # Remove the oldest reports which are the first 'excess_count' elements
            for report in reports_folders[:excess_count]:
                print(f"Removing {report.name} ...")
                shutil.rmtree(report)
        print("Cleanup done.")

    @cached_property
    def root_url(self) -> str:
        """Get URL to the root of reports."""
        if not self.inputs.website_url:
            repository_name = self.env.github_repository.split("/")[-1]  # owner/repo
            url = f"https://{self.env.github_repository_owner}.github.io/{repository_name}"
        else:
            url = self.inputs.website_url
        if self.inputs.reports_site_path:
            return "/".join([url, self.inputs.reports_site_path])
        return url

    @cached_property
    def last_report_file_url(self) -> str:
        """Get URL to the last report."""
        return "/".join([self.root_url, self.env.github_run_number]) + "/index.html"

    def report_page(self) -> str:
        """Get the report page part of the url."""
        return f"#{self.inputs.report_page}" if self.inputs.report_page else ""

    def create_index_html(self) -> None:
        """Create index.html in the report folder root with redirect to the last report."""
        template = self.environment.get_template("index.html")
        rendered_template = template.render(url=f"{self.last_report_file_url}{self.report_page()}")
        (self.reports_site / "index.html").write_text(rendered_template)

    def generate_allure_report(self) -> None:
        """Prepare params and Call allure generate."""
        template = self.environment.get_template("executor.json")
        # https://allurereport.org/docs/how-it-works-executor-file/
        rendered_template = template.render(
            report_url=self.last_report_file_url,
            report_name=self.render(self.inputs.report_name),
            ci_name=self.render(self.inputs.ci_name),
            github_run_number=self.env.github_run_number,
            github_server_url=self.env.github_server_url,
            github_run_id=self.env.github_run_id,
            github_repository=self.env.github_repository,
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
                str(self.reports_site / self.env.github_run_number),
            ],
            check=True,
        )

        shutil.copytree(
            self.reports_site / self.env.github_run_number / "history",
            self.reports_site / "last-history",
            dirs_exist_ok=True,
        )
        print("Report generated.")


if __name__ == "__main__":  # pragma: no cover
    AllureGenerator().run()
    print("All done.")
