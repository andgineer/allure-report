import os
from pathlib import Path
from unittest.mock import patch, call
from src.allure_generate import AllureGenerator


def test_create_directories(tmpdir, env):
    result_file_name = "18e5c48c-ca67-4842-91d1-01af64bd4488-result.json"
    allure_gen = AllureGenerator()
    allure_gen.site_source = Path(tmpdir) / "site-source"
    allure_gen.allure_history = Path(tmpdir) / "allure-history"
    (allure_gen.site_source / allure_gen.site_path).mkdir(parents=True, exist_ok=True)
    with (allure_gen.site_source / allure_gen.site_path / result_file_name).open("w"):
        pass

    with patch("subprocess.run") as mock_run:
        allure_gen.run()

        assert allure_gen.site_source.exists()
        assert allure_gen.allure_history.exists()
        assert (allure_gen.allure_history / result_file_name).exists()

        expected_calls = [
            call(
                [
                    "allure",
                    "generate",
                    "--clean",
                    str(allure_gen.allure_results),
                    "-o",
                    str(allure_gen.allure_report),
                ]
            )
        ]
        mock_run.assert_has_calls(expected_calls)


def test_generate_index_html(tmpdir, expected_index_file, env):
    allure_gen = AllureGenerator()
    allure_gen.allure_history = Path(tmpdir) / "allure-history"
    allure_gen.allure_history.mkdir(parents=True, exist_ok=True)

    allure_gen.generate_index_html("https://example.com")

    with open(os.path.join(allure_gen.allure_history, "index.html"), "r") as f:
        assert expected_index_file.read() == f.read()
