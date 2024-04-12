import os
import shutil
import subprocess
from functools import cached_property
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from .__about__ import __version__


class AllureGenerator:
    def __init__(self):
        print(f"Generate Allure Report action v.{__version__}")

        self.github_repository = os.getenv("GITHUB_REPOSITORY")
        self.github_repository_owner = os.getenv("GITHUB_REPOSITORY_OWNER")
        self.github_server_url = os.getenv("GITHUB_SERVER_URL")
        self.github_run_number = os.getenv("GITHUB_RUN_NUMBER")
        self.github_run_id = os.getenv("GITHUB_RUN_ID")

        # Action inputs
        self.allure_results = Path(self.get_input("allure-results"))
        self.website_source = Path(self.get_input("website-source"))
        self.report_path = self.get_input("report-path")
        self.allure_report = Path(self.get_input("allure-report"))
        self.website_url = self.get_input("website-url")
        self.report_name = self.get_input("report-name")
        self.ci_name = self.get_input("ci-name")
        self.max_history_reports = (
            int(self.get_input("max-reports")) if self.get_input("max-reports") else 0
        )

        base_dir = Path(__file__).resolve().parent
        templates_dir = base_dir / "templates"
        self.environment = Environment(loader=FileSystemLoader(str(templates_dir)))

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

    def get_input(self, name):
        return os.getenv(f"INPUT_{name.upper()}")

    def run(self):
        self.cleanup_reports()
        self.generate_allure_report()
        self.create_index_html()

    def cleanup_reports(self):
        # in site report folder each report is stored in a separate sub folder
        reports_count = len(
            [
                f
                for f in self.prev_report.glob("*")
                if f.name not in ["index.html", "CNAME"]
            ]
        )
        if (
            self.max_history_reports
            and reports_count
            > self.max_history_reports  # already excluding index.html and CNAME
        ):
            print(
                f"Found {reports_count} reports in history, keeping only {self.max_history_reports}"
            )
            for report in reports_count[: -self.max_history_reports]:
                report.unlink()

    @cached_property
    def last_report_url(self):
        url_parts = [self.website_url, self.github_run_number, "index.html"]
        if self.report_path:
            url_parts.insert(1, self.report_path)
        return "/".join(url_parts)

    def create_index_html(self):
        """Create index.html in the report folder root with redirect to the last report."""
        template = self.environment.get_template("index.html")
        rendered_template = template.render(url=self.last_report_url)
        (self.allure_report / "index.html").write_text(rendered_template)

    def generate_allure_report(self):
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
        (self.allure_report / "executor.json").write_text(rendered_template)

        # https://allurereport.org/docs/how-it-works-history-files/
        (self.prev_report / "last-history").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            self.prev_report / "last-history",
            self.allure_results / "history",
            dirs_exist_ok=True,
        )

        print(
            f"Generating report from {self.allure_report} to {self.allure_report} ..."
        )
        subprocess.run(
            [
                "allure",
                "generate",
                "--clean",
                str(self.allure_results),
                "-o",
                str(self.allure_report / self.github_run_number),
            ]
        )

        (self.allure_report / self.github_run_number / "history").mkdir(
            parents=True, exist_ok=True
        )  # move to test?
        shutil.copytree(
            self.allure_report / self.github_run_number / "history",
            self.allure_report / "last-history",
            dirs_exist_ok=True,
        )


if __name__ == "__main__":
    generator = AllureGenerator()
    generator.run()
