import os
from unittest.mock import MagicMock, patch, PropertyMock
import pytest
from pathlib import Path
from src.allure_generate import AllureGenerator


@pytest.fixture
def generator(env):  # Utilizes the 'env' fixture for setting up the environment
    # Setup the Path mocking
    with patch('pathlib.Path.glob') as mock_glob, \
            patch('pathlib.Path.mkdir'), \
            patch('shutil.rmtree', autospec=True) as mock_shutil_rmtree:
        reports = []
        for i in range(5, 12):
            report = MagicMock(spec=Path, is_dir=MagicMock(return_value=True))
            type(report).name = PropertyMock(return_value=str(i))
            mock_stat = MagicMock()
            mock_stat.st_mtime = i  # Use a simple integer for sorting
            report.stat = MagicMock(return_value=mock_stat)
            reports.append(report)

        exclusions = [
            MagicMock(spec=Path, is_dir=MagicMock(return_value=False)) for _ in range(2)
        ]
        type(exclusions[0]).name = PropertyMock(return_value='index.html')
        type(exclusions[1]).name = PropertyMock(return_value='CNAME')

        all_files = reports + exclusions
        mock_glob.return_value = all_files

        gen = AllureGenerator()
        gen.max_history_reports = 5
        yield gen, all_files, mock_shutil_rmtree


def test_deletion_of_excess_reports(generator):
    gen, reports, mock_shutil_rmtree = generator
    gen.cleanup_reports()
    # Check the number of unlink calls
    deleted_reports = [report for call_args in mock_shutil_rmtree.call_args_list for report in reports if call_args[0][0] == report]
    assert len(deleted_reports) == 2  # 7 reports - 5 allowed = 2 should be deleted
    assert deleted_reports[0].name == '5'
    assert deleted_reports[1].name == '6'


def test_no_reports_to_delete(generator):
    gen, reports, _ = generator
    # All reports fit within the history limit
    gen.max_history_reports = 7
    gen.cleanup_reports()
    assert all(not report.unlink.called for report in reports)


def test_no_reports_at_all(generator):
    gen, reports, _ = generator
    # Mock no reports being present
    gen.prev_reports.glob.return_value = []
    gen.cleanup_reports()
    assert all(not report.unlink.called for report in reports)


def test_non_directory_files(generator):
    gen, reports, _ = generator
    # All files are not directories
    for report in reports:
        report.is_dir.return_value = False
    gen.cleanup_reports()
    assert all(not report.unlink.called for report in reports)


def test_invalid_max_reports_settings(env):
    with patch.dict(os.environ, {"INPUT_MAX-REPORTS": "-1"}):
        with pytest.raises(ValueError, match="max-reports cannot be negative."):
            AllureGenerator()


def test_unlimit_reports_settings(generator):
    gen, reports, _ = generator
    gen.max_history_reports = 0
    gen.cleanup_reports()
    assert all(not report.unlink.called for report in reports)


def test_empty_path_input(env):
    with patch.dict(os.environ, {"INPUT_ALLURE-RESULTS": ""}):
        with pytest.raises(ValueError, match="Parameter `allure-results` cannot be empty."):
            AllureGenerator()


def test_inplace_reports(env):
    with patch.dict(os.environ, {"INPUT_REPORTS-SITE": ""}):
        gen = AllureGenerator()
        assert gen.reports_site == gen.prev_reports
        assert (gen.reports_site / "22" / "index.html").exists()


def test_website_folder_unexisted(env):
    with patch.dict(os.environ, {"INPUT_WEBSITE": "-unexisted-"}):
        with patch("subprocess.run"):
            gen = AllureGenerator()
            (gen.reports_site / gen.env.github_run_number / "history").mkdir(
                parents=True, exist_ok=True
            )
            gen.run()
        assert not (gen.reports_site / "22").exists()
        assert (gen.reports_site / "index.html").exists()
        assert not (gen.reports_site / "22").exists()


def test_no_summary(env):
    with patch.dict(os.environ, {"INPUT_SUMMARY": ""}):
        with patch("subprocess.run"):
            gen = AllureGenerator()
            (gen.reports_site / gen.env.github_run_number / "history").mkdir(
                parents=True, exist_ok=True
            )
            gen.run()
        assert gen.env.github_step_summary.read_text() == ""


def test_summary(env):
    with patch("subprocess.run"):
        gen = AllureGenerator()
        (gen.reports_site / gen.env.github_run_number / "history").mkdir(
            parents=True, exist_ok=True
        )
        gen.run()
    assert "github.io" in gen.outputs["report-url"]
    assert gen.outputs["report-url"] in gen.env.github_output.read_text()
    assert f"reports-site-path=builds/tests" in gen.env.github_output.read_text()
    assert "reports-root-url=https://owner.github.io/repo" in gen.env.github_output.read_text()
