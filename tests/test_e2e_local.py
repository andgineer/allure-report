"""Local e2e tests.

Mock allure generate.
"""

import os
import shutil

from pathlib import Path
from unittest.mock import patch, call
from src.allure_generate import AllureGenerator
from src.__about__ import __version__


def test_create_directories(capsys, env, expected_index_file, expected_executor_file):
    allure_gen = AllureGenerator()
    shutil.rmtree(allure_gen.reports_site, ignore_errors=True)
    (allure_gen.inputs.allure_results / "executor.json").unlink(missing_ok=True)
    shutil.rmtree(allure_gen.inputs.allure_results / "history", ignore_errors=True)
    (allure_gen.reports_site / "1" / "history").mkdir(parents=True, exist_ok=True)
    with patch("subprocess.run") as mock_subprocess:
        allure_gen.run()

        assert (allure_gen.inputs.allure_results / "history" / "history.json").exists(), (
            "History not copied"
        )
        assert (
            allure_gen.inputs.allure_results / "executor.json"
        ).read_text() == expected_executor_file.read()
        assert (allure_gen.reports_site / "index.html").read_text() == expected_index_file.read()
        assert (allure_gen.reports_site / "22" / "index.html").exists(), (
            "Previous reports not copied"
        )

        expected_calls = [
            call(
                [
                    "allure",
                    "generate",
                    "--clean",
                    str(allure_gen.inputs.allure_results),
                    "-o",
                    str(allure_gen.reports_site / allure_gen.env.github_run_number),
                ],
                check=True,
            )
        ]
        mock_subprocess.assert_has_calls(expected_calls)

        captured = capsys.readouterr().out
        assert __version__ in captured, (
            f"Expected a call with `{__version__}` not found in print calls"
        )

        last_report_url = "https://owner.github.io/repo/builds/tests/1/index.html#behavior"
        assert f"report-url={last_report_url}" in Path(os.environ["GITHUB_OUTPUT"]).read_text()
