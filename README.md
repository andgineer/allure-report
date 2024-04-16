[![Build Status](https://github.com/andgineer/allure-report/workflows/CI/badge.svg)](https://github.com/andgineer/allure-report/actions)
[![Coverage](https://raw.githubusercontent.com/andgineer/allure-report/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/allure-report/blob/python-coverage-comment-action-data/htmlcov/index.html)
# GitHub Action to generate Allure Report

A GitHub Action that generates a visually stunning Allure test report.

[The report](https://andgineer.github.io/bitwarden-import-msecure/builds/tests/94/index.html#) 
also show history of previous tests results with links to them.

## Usage

### Checkout reports history

This is optional but useful part.

We can skip it if we don't need to keep the history of the reports and do not want to show the history of
individual tests in the Allure report.

If your github pages are in default `gh-pages` branch, to checkout them to
folder `gh-pages-dir` use:

```yaml
    - name: Checkout github pages with previous Allure reports
      uses: actions/checkout@v4
      with:
        ref: gh-pages
        path: gh-pages-dir

```

### Run tests with writing Allure results

In case of Python install `allure-pytest` package and use `--alluredir=./allure-results` option to save results to 
`allure-results` folder.

```yaml
    - name: Install pytest Allure plugin
      run: pip install allure-pytest
    - name: Test with generating Allure results
      run: pytest --alluredir=./allure-results tests/
```

### Generating Allure report

This is where we need the action.

`website` is the directory with our website, in our case this is `gh-pages-dir`.

`reports-site-path` is where the reports located in the website, empty if in root.

The Allure report will be created inplace in the `website` / `reports-site-path`, in separate folder named as 
github run number.

In the root of `website` / `reports-site-path` will be created `index.html` that auto-redirect to the last report.

Note we use `if: always()` to create report even if the tests failed.

```yaml
    - name: Generate Allure test report
      uses: andgineer/allure-report@v1.6
      id: allure-report
      if: always()
      with:
        allure-results: allure-results
        website: gh-pages-dir
        reports-site-path: builds/tests
```

### Publish the report back to the github pages

For example we can use this action:

```yaml
    - name: Publish Allure test report
      uses: peaceiris/actions-gh-pages@v3
      if: ${{ always() && (steps.allure-report.outcome == 'success') }}
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_branch: gh-pages
        publish_dir: ${{ steps.allure-report.outputs.REPORTS_SITE }}
        destination_dir: ${{ steps.allure-report.outputs.REPORTS_SITE_PATH }}
```

We use outputs of the previous action so no need to copy&past your paths.

# Example

See full example in the
[test with report workflow](https://github.com/andgineer/bitwarden-import-msecure/blob/main/.github/workflows/ci.yml)

# Important note

If you also publish some site to the same github pages, make sure you backup the reports 
so the site publishing won't delete them.
See example in [creating docs with reports backup](https://github.com/andgineer/bitwarden-import-msecure/blob/main/.github/workflows/docs.yml)

## Limitations

As Dockerfile action runs only on Linux runners.

## Inputs

| Name              | Description                                                                                                                                                                                                   | Required | Default                               |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------------------------------------|
| allure-results    | Allure test result directory created by tests.                                                                                                                                                                | true     | allure-results                        |
| website    | Website directory (e.g., checkouted from the gh-pages branch).                                                                                                                                                | false    | gh-pages-dir                          |
| reports-site-path | Allure report path within the website.                                                                                                                                                                        | false    | builds/tests                          |
| reports-site      | Allure reports directory, to be pushed to the website repository at the `reports-site-path`. Each report on the subfolder with the github run number. If specified the old reports copied from `website`. | false    | [create report inplace in `website`/`reports-site-path`] |
| website-url       | Custom URL to use instead of the default GitHub Pages URL for the website where Allure report will be published                                                                                               | false    |                                       |
| report-name       | The name to be shown on top of the Overview tab in the Allure report                                                                                                                                          | false    | Allure Test Report                    |
| ci-name           | The name of the CI server                                                                                                                                                                                     | false    | GitHub Action: {{ github.workflow }}  |
| max-reports       | Number of previous Allure reports to keep. Set to 0 to keep all reports.                                                                                                                                      | false    | 20                                    |

## Outputs

| Name              | Description                                                               | 
|-------------------|---------------------------------------------------------------------------|
| REPORT_URL        | URL of the created report                                                 | 
| REPORTS_ROOT_URL  | Root of all reports with index.html that auto-redirect to the last report |
| REPORTS_SITE_PATH | Copy of input reports-site-path for convenience use in next actions       |
| REPORTS_SITE | Copy of input reports-site for convenience use in next actions            |


## Development

To create/activate a virtual environment (note the space between the two dots):

    . ./activate.sh

For formatting and linting install pre-commit hooks:

    pre-commit install

Tests uses local docker-compose to run the action.
It sets env vars like in Github action environment (from `tests/resources/.env` file)

   python -m pytest tests/

You can run the action in the Docker locally with:

    inv run
    inv logs

for experiments inside the container use:

    inv container

All the commands
    
    inv --list

## Coverage report
* [Coveralls](https://coveralls.io/github/andgineer/allure-report)