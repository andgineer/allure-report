import os
import shutil
from pathlib import Path
from unittest.mock import patch, call
from src.allure_generate import AllureGenerator


def test_create_directories(env, expected_index_file, expected_executor_file):
    result_file_name = "18e5c48c-ca67-4842-91d1-01af64bd4488-result.json"
    allure_gen = AllureGenerator()
    shutil.rmtree(allure_gen.allure_report, ignore_errors=True)
    (allure_gen.allure_results / "executor.json").unlink(missing_ok=True)
    shutil.rmtree(allure_gen.allure_results / "history", ignore_errors=True)

    with patch("subprocess.run") as mock_run:
        allure_gen.run()

        assert (allure_gen.allure_report / "index.html").read_text() == expected_index_file.read()
        assert (allure_gen.allure_results / "executor.json").read_text() == expected_executor_file.read()
        assert (allure_gen.allure_report / allure_gen.github_run_number / "history").exists()
        # assert (allure_gen.allure_report / "22" / "index.html").exists()

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
