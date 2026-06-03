# Plan: Include run attempt in report folder name [DONE]

## Context

Re-runs of the same workflow share the same `GITHUB_RUN_NUMBER`, so each re-run overwrites the previous attempt's report folder. The fix is to append `GITHUB_RUN_ATTEMPT` to the folder name by default (`<run_number>-<attempt>`), producing distinct folders per attempt with no new input parameter. Old folders named `<run_number>` (pure digits) must continue to work: the cleanup regex is widened to match both formats, and old folders age out naturally under `max-reports`.

## Changes

### 1. `src/allure_generate.py`

**Add `run_folder_name` cached property** on `AllureGenerator`:
```python
@cached_property
def run_folder_name(self) -> str:
    return f"{self.env.github_run_number}-{self.env.github_run_attempt}"
```

**Replace folder references** — every place that uses `self.env.github_run_number` as a folder path must use `self.run_folder_name` instead:
- `last_report_file_url` (line 152): `self.env.github_run_number` → `self.run_folder_name`
- `generate_allure_report` (lines 192, 201): both occurrences of `self.env.github_run_number` used as a path segment → `self.run_folder_name`

Note: the `github_run_number` passed to the `executor.json` template (line 172) stays as-is — that's metadata shown in the report UI, not a folder name.

**Update `cleanup_reports`** (lines 117, 128):
- Regex: `r"^\d+$"` → `r"^\d+(-\d+)?$"` — matches both `123` (old) and `123-2` (new)
- Sort key: `int(x.name)` → `int(x.name.split("-")[0])` — sort by run number prefix regardless of suffix

### 2. `tests/conftest.py`

Add `"GITHUB_RUN_ATTEMPT": "1"` to the `env_vars` dict in the `env` fixture.

### 3. `tests/test_allure_report.py`

**Fix history dir creation** in three tests that currently do:
```python
(gen.reports_site / gen.env.github_run_number / "history").mkdir(...)
```
Change to `gen.run_folder_name` so the directory the test creates matches what the action will look for:
- `test_website_folder_unexisted`
- `test_no_summary`
- `test_summary`

**Add two new test cases:**
- `test_run_folder_name_includes_attempt` — assert `gen.run_folder_name == "1-1"` given the env fixture defaults (`GITHUB_RUN_NUMBER=1`, `GITHUB_RUN_ATTEMPT=1`)
- `test_cleanup_mixed_old_and_new_folders` — generator fixture with a mix of old-style (`"5"`, `"6"`) and new-style (`"7-1"`, `"8-2"`) folder names; verify cleanup sorts and prunes correctly

## Verification

```bash
source ./activate.sh && python -m pytest tests/test_allure_report.py -v
source ./activate.sh && inv pre
```

For a live check, `inv run` + `inv logs` to confirm the generated folder name inside the container matches `<run_number>-<attempt>`.
