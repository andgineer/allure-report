[![Build Status](https://github.com/andgineer/allure-report/workflows/CI/badge.svg)](https://github.com/andgineer/allure-report/actions)
[![Coverage](https://raw.githubusercontent.com/andgineer/allure-report/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/allure-report/blob/python-coverage-comment-action-data/htmlcov/index.html)
# GitHub Action to generate Allure Report

Generates a visually stunning [Allure test report](https://andgineer.github.io/bitwarden-import-msecure/builds/tests/94/index.html#).
The report show history of previous tests results with links to them.

Could be published on the GitHub Pages or any other static web server.

## Usage

### Checkout git hub pages

We can skip the step if we don't want to show the history of
tests in the Allure report.

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
      run: pip install pytest allure-pytest
    - name: Test with generating Allure results
      run: pytest --alluredir=./allure-results tests/
```

### Generating Allure report

This is where we need the action.

```yaml
    - name: Generate Allure test report
      uses: andgineer/allure-report@v1.7
      id: allure-report
      if: always()
      with:
        allure-results: allure-results
        website: gh-pages-dir
        reports-site-path: builds/tests
```

`website` is the directory with our website.

`reports-site-path` is where the reports located in the website, empty if in root.

The Allure report will be created inplace in the `website` / `reports-site-path`, in separate folder named as 
github run number.

In the root of `website` / `reports-site-path` will be created `index.html` that auto-redirect to the last report.

Note we use `if: always()` to create report even if the tests failed.

### Publish the report back to the github pages

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

We use outputs of the previous step so no need to copy&past your paths.

#### Example

See full example in the
[test with report workflow](https://github.com/andgineer/bitwarden-import-msecure/blob/main/.github/workflows/ci.yml)

#### Important note

If you also publish some site to the same github pages, make sure you backup the reports 
so the site publishing won't delete them.
See example in [creating docs with reports backup](https://github.com/andgineer/bitwarden-import-msecure/blob/main/.github/workflows/docs.yml)

## Limitations

This is Dockerfile action, so it runs only on Linux runners.

## Inputs

| Name              | Description                                                                                                                                           | Default                                                             |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| allure-results    | Allure test result directory created by tests.                                                                                                        | allure-results                                                      |
| website    | Website directory (e.g., checkouted from the gh-pages branch).                                                                                        | gh-pages-dir                                                        |
| reports-site-path | Allure report path within the website.                                                                                                                | builds/tests                                                        |
| reports-site      | Allure reports directory, to be pushed to the website repository at the `reports-site-path`. If specified the old reports copied here from `website`. | [create report inplace in `website`/`reports-site-path`]            |
| website-url       | Custom URL to use instead of the default GitHub Pages URL for the website where Allure report will be published                                       |                                                                     |
| report-name       | The name to be shown on top of the Overview tab in the Allure report                                                                                  | Allure Test Report                                                  |
| ci-name           | The name of the CI server                                                                                                                             | GitHub Action: {{ vars.github_workflow }}                           |
| max-reports       | Number of previous Allure reports to keep. Set to 0 to keep all reports.                                                                              | 20                                                                  |
|   summary | Summary text for the action to be shown in the GitHub Actions UI. Set to empty string to disable. | \n## Test report\n[Allure test report]({{ outputs["REPORT_URL"] }})\n\n |

## Outputs

| Name              | Description                                                                              | 
|-------------------|------------------------------------------------------------------------------------------|
| REPORT_URL        | URL of the created report                                                                | 
| REPORTS_ROOT_URL  | Root of all reports with index.html that auto-redirect to the last report                |
| REPORTS_SITE_PATH | Copy of input reports-site-path                      |
| REPORTS_SITE | Folder where the reports located. To be published in `reports-site-path` in your website |

## Working details

Report is generated from [Allure results](https://allurereport.org/docs/how-it-works/) 
folder specified in `allure-results`.

Read the Allure docs to know how to create them. 
For example, in Python, you can use `allure-pytest` package. 
It adds to `pytest` option `--alluredir`. 
So to generate Allure results in `allure-pytest`, use `pytest --alluredir=./allure-results`.

History reports expected in `website` / `reports-site-path`.

If `allure-report` is specified, the history reports is copied to it and the new report generated in it. 
Otherwise, the report is generated inplace in the `website` / `reports-site-path`.

Each report is stored in folder with the github run number.

In the root of the reports folder the action creates `index.html` with redirect to the last report.

All specified in action input folders could do not exist, they will be created if needed.

In output `REPORTS_SITE` will be folder to publish on the `reports-site-path` in your website. 
This is subfolder `reports-site-path` of the `website`, or `reports-site` if it was specified.

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