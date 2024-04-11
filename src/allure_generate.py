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
        self.report_name = self.get_input("report-name")
        self.ci_name = self.get_input("ci-name")
        self.site_source = Path(self.get_input("site-source"))
        self.allure_history = Path(self.get_input("allure-history"))
        self.allure_results = Path(self.get_input("allure-results"))
        self.allure_report = Path(self.get_input("allure-report"))
        self.site_path = self.get_input("site-path")
        self.site_url = self.get_input("site-url")
        self.number_reports_to_keep = (
            int(self.get_input("number-reports-to-keep"))
            if self.get_input("number-reports-to-keep")
            else 0
        )

    def get_input(self, name):
        return os.getenv(f"INPUT_{name.upper().replace('-', '_')}")

    def run(self):
        repository_name = self.github_repository.split("/")[-1]  # owner/repo
        site_url = f"https://{self.github_repository_owner}.github.io/{repository_name}"
        if self.site_url:
            site_url = self.site_url
            print(f"User defined site url: {site_url}")

        if self.site_path:
            # Report not in the root of the site
            self.allure_history = self.allure_history / self.site_path
            self.site_source = self.site_source / self.site_path
            print(f"Allure history subfolder: {self.allure_history}")
            site_url = f"{site_url}/{self.site_path}"
            print(f"Site url: {site_url}")

        self.allure_history.mkdir(parents=True, exist_ok=True)
        self.site_source.mkdir(parents=True, exist_ok=True)

        shutil.copytree(self.site_source, self.allure_history, dirs_exist_ok=True)

        reports_in_history = len(list(self.allure_history.glob("*")))
        if (
            self.number_reports_to_keep
            and reports_in_history > self.number_reports_to_keep
        ):
            self.cleanup_reports_history()

        self.generate_index_html(site_url)

        print(
            f"keep allure history from {self.site_source}/last-history to {self.allure_results}/history"
        )
        (self.site_source / "last-history").mkdir(parents=True, exist_ok=True)
        (self.allure_results / "history").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            self.site_source / "last-history",
            self.allure_results / "history",
            dirs_exist_ok=True,
        )

        self.generate_allure_report(site_url)

        print(f"Copy Allure report to {self.allure_history}/{self.github_run_number}")
        self.allure_report.mkdir(parents=True, exist_ok=True)  # move to test?
        shutil.copytree(
            self.allure_report,
            self.allure_history / self.github_run_number,
            dirs_exist_ok=True,
        )

        print(f"Copy Allure report history to {self.allure_history}/last-history")
        (self.allure_report / "history").mkdir(
            parents=True, exist_ok=True
        )  # move to test?
        shutil.copytree(
            self.allure_report / "history",
            self.allure_history / "last-history",
            dirs_exist_ok=True,
        )

    def cleanup_reports_history(self):
        print("Removing old reports")
        (self.allure_history / "index.html").unlink(missing_ok=True)
        (self.allure_history / "last-history").unlink(missing_ok=True)
        reports = sorted(list(self.allure_history.glob("*")))
        for report in reports[
            : -self.number_reports_to_keep + 2  # keep CNAME and todo:?
        ]:
            if report.name != "CNAME":
                report.unlink()

    def generate_index_html(self, url):
        template = self.environment.get_template("index.html")
        rendered_template = template.render(
            url=url, github_run_number=self.github_run_number
        )
        (self.allure_history / "index.html").write_text(rendered_template)

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
        (self.allure_results / "executor.json").write_text(rendered_template)

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
                str(self.allure_report),
            ]
        )


if __name__ == "__main__":
    generator = AllureGenerator()
    generator.run()
