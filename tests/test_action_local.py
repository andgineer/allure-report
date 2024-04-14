import os
import shutil
from pathlib import Path
from unittest.mock import patch, call
from src.allure_generate import AllureGenerator


def test_create_directories(env, expected_index_file, expected_executor_file):
    allure_gen = AllureGenerator()
    shutil.rmtree(allure_gen.allure_report, ignore_errors=True)
    (allure_gen.allure_results / "executor.json").unlink(missing_ok=True)
    shutil.rmtree(allure_gen.allure_results / "history", ignore_errors=True)
    (allure_gen.allure_report / "1" / "history").mkdir(
        parents=True, exist_ok=True
    )

    with patch("subprocess.run") as mock_run, patch('builtins.print') as mock_print:
        allure_gen.run()

        assert (allure_gen.allure_results / "history" / "history.json").exists(), "History not copied"
        assert (allure_gen.allure_results / "executor.json").read_text() == expected_executor_file.read()
        assert (allure_gen.allure_report / "index.html").read_text() == expected_index_file.read()
        assert (allure_gen.allure_report / "22" / "index.html").exists(), "Previous reports not copied"

        expected_calls = [
            call(
                [
                    "allure",
                    "generate",
                    "--clean",
                    str(allure_gen.allure_results),
                    "-o",
                    str(allure_gen.allure_report / allure_gen.github_run_number),
                ],
                check=True,
            )
        ]
        mock_run.assert_has_calls(expected_calls)
        last_report_url = "https://owner.github.io/repo/test-report/1/index.html"
        mock_print.assert_called_with(f"::set-output name=REPORT_URL::{last_report_url}")
