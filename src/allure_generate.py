import os
import shutil
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class AllureGenerator:
    def __init__(self):
        self.github_repository = os.getenv("GITHUB_REPOSITORY")
        self.github_repository_owner = os.getenv("GITHUB_REPOSITORY_OWNER")
        self.github_server_url = os.getenv("GITHUB_SERVER_URL")
        self.github_run_number = os.getenv("GITHUB_RUN_NUMBER")
        self.github_run_id = os.getenv("GITHUB_RUN_ID")

        self.environment = Environment(loader=FileSystemLoader("templates"))

        # Action inputs
        self.allure_results = Path(self.get_input("allure-results"))
        self.website_source = Path(self.get_input("website-source"))
        self.report_path = self.get_input("report-path")
        self.allure_report = Path(self.get_input("allure-report"))
        self.website_url = self.get_input("website-url")
        self.report_name = self.get_input("report-name")
        self.ci_name = self.get_input("ci-name")
        self.max_history_reports = (
            int(self.get_input("max-history-reports"))
            if self.get_input("max-history-reports")
            else 0
        )

        self.prev_report = self.website_source / self.report_path if self.report_path else self.website_source
        print(f"Prev report in: {self.prev_report}")
        self.prev_report.mkdir(parents=True, exist_ok=True)

    def get_input(self, name):
        return os.getenv(f"INPUT_{name.upper().replace('-', '_')}")

    def run(self):
        repository_name = self.github_repository.split("/")[-1]  # owner/repo
        site_url = f"https://{self.github_repository_owner}.github.io/{repository_name}"
        if self.website_url:
            site_url = self.website_url
            print(f"User defined site url: {site_url}")

        self.cleanup_reports_history()

        self.generate_index_html(site_url)

        # https://allurereport.org/docs/how-it-works-history-files/
        print(
            f"keep allure history from {self.prev_report}/last-history in {self.allure_report}/history"
        )
        (self.prev_report / "last-history").mkdir(parents=True, exist_ok=True)
        (self.allure_report / "history").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            self.prev_report / "last-history",
            self.allure_results / "history",
            dirs_exist_ok=True,
        )

        self.generate_allure_report(site_url)

        print(f"Copy Allure report history to {self.allure_report}/last-history")
        (self.allure_report / self.github_run_number / "history").mkdir(
            parents=True, exist_ok=True
        )  # move to test?
        shutil.copytree(
            self.allure_report / self.github_run_number / "history",
            self.allure_report / "last-history",
            dirs_exist_ok=True,
        )

    def cleanup_reports_history(self):
        # in site report folder each report is stored in a separate sub folder
        reports_in_history = len([f for f in self.prev_report.glob("*") if f.name not in ["index.html", "CNAME"]])
        if (
                self.max_history_reports
                and reports_in_history > self.max_history_reports  # already excluding index.html and CNAME
        ):
            print("Removing old reports")
            for report in reports_in_history[
                          : -self.max_history_reports
                          ]:
                report.unlink()

    def generate_index_html(self, url):
        template = self.environment.get_template("index.html")
        rendered_template = template.render(
            url=url, github_run_number=self.github_run_number
        )
        (self.allure_report / "index.html").write_text(rendered_template)

    def generate_allure_report(self, site_url):
        template = self.environment.get_template("executor.json")
        # https://allurereport.org/docs/how-it-works-executor-file/
        rendered_template = template.render(
            url=site_url,
            report_name=self.report_name,
            ci_name=self.ci_name,
            github_run_number=self.github_run_number,
            github_server_url=self.github_server_url,
            github_run_id=self.github_run_id,
            github_repository=self.github_repository,
        )
        (self.allure_report / "executor.json").write_text(rendered_template)

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


if __name__ == "__main__":
    generator = AllureGenerator()
    generator.run()
