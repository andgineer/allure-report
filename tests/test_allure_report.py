import os
from unittest.mock import MagicMock, patch, PropertyMock
import pytest
from pathlib import Path
from src.allure_generate import AllureGenerator  # Update imports as necessary


@pytest.fixture
def generator(env):  # Utilizes the 'env' fixture for setting up the environment
    # Setup the Path mocking
    with patch('pathlib.Path.glob') as mock_glob, \
            patch('pathlib.Path.mkdir'), \
            patch('pathlib.Path.unlink', autospec=True) as mock_unlink:
        reports = []
        for i in range(1, 8):
            report = MagicMock(spec=Path, is_dir=MagicMock(return_value=True))
            type(report).name = PropertyMock(return_value=f'report{i}')
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
        yield gen, all_files


def test_deletion_of_excess_reports(generator):
    gen, reports = generator
    gen.cleanup_reports()
    # Check the number of unlink calls
    deleted_reports = [report for report in reports if report.unlink.called]
    assert len(deleted_reports) == 2  # 7 reports - 5 allowed = 2 should be deleted

    # Optionally check specific reports
    assert reports[0].unlink.called  # Assuming report1 is the oldest, based on your sorting logic
    assert reports[1].unlink.called


def test_no_reports_to_delete(generator):
    gen, reports = generator
    # All reports fit within the history limit
    gen.max_history_reports = 7
    gen.cleanup_reports()
    assert all(not report.unlink.called for report in reports)


def test_no_reports_at_all(generator):
    gen, reports = generator
    # Mock no reports being present
    gen.prev_report.glob.return_value = []
    gen.cleanup_reports()
    assert all(not report.unlink.called for report in reports)


def test_non_directory_files(generator):
    gen, reports = generator
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
    gen, reports = generator
    gen.max_history_reports = 0
    gen.cleanup_reports()
    assert all(not report.unlink.called for report in reports)

def test_default_ci_name(env):
    with patch.dict(os.environ, {"INPUT_CI-NAME": ""}):
        gen = AllureGenerator()
        assert gen.ci_name == "GitHub Action: CI/CD"
