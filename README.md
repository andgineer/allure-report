[![Build Status](https://github.com/andgineer/allure-report/workflows/CI/badge.svg)](https://github.com/andgineer/allure-report/actions)
[![Coverage](https://raw.githubusercontent.com/andgineer/allure-report/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/allure-report/blob/python-coverage-comment-action-data/htmlcov/index.html)
# GitHub Action to generate Allure Report

A GitHub Action that generates a visually stunning Allure test report.

## Usage

After usual checkout of your project you should checkout github pages 
where we are publishing the Allure report. 

If your github pages are in default `gh-pages` branch, to checkout them to
folder `gh-pages` use:

```yaml
    - name: Checkout github pages with previous Allure reports
      uses: actions/checkout@v4
      with:
        ref: gh-pages
        path: gh-pages-dir

```

Then run tests with writing Allure results.
For that install `allure-pytest` and use `--alluredir=./allure-results` option to save results to 
`allure-results` folder.

```yaml
    - name: Install pytest Allure plugin
      run: pip install allure-pytest
    - name: Test with generating Allure results
      run: pytest --alluredir=./allure-results tests/
```

Now we are ready for the main part - generating and publishing the Allure report.

Description of the action input see below in `Inputs`. 

`reports-site-path` is where our report located in the website. 
We use that path to get previous report from `website-source`, and to create redirect from the root
to the last report.

As a result of the action we will have in folder `reports-site` new Allure report as well as previous 
(up to `max-reports`).

Note `if: always()` to create report even if the tests failed.

```yaml
    - name: Generate Allure test report
      uses: andgineer/allure-report@v1.5
      id: allure-report
      if: always()
      with:
        website-source: gh-pages-dir
        allure-results: allure-results
        reports-site: reports-site
        reports-site-path: builds/tests
```

To publish the report on the github pages you can use whatever action you like.
For example:

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

See full example in
[the workflow](https://github.com/andgineer/bitwarden-import-msecure/blob/main/.github/workflows/ci.yml)

If you also publish some site to the github pages, make sure you backup the reports so the site publishing won't delete them.
See example in [the workflow](https://github.com/andgineer/bitwarden-import-msecure/blob/main/.github/workflows/docs.yml)

## Limitations

As Dockerfile action runs only on Linux runners.

## Inputs

| Name              | Description                                                                                                     | Required | Default                              |
|-------------------|-----------------------------------------------------------------------------------------------------------------|----------|--------------------------------------|
| allure-results    | Allure test result directory created by tests.                                                                  | true     | allure-results                       |
| website-source    | Website checkout location (e.g., from the gh-pages branch).                                                     | true     | gh-pages                             |
| reports-site-path | Allure report path within the website.                                                                          | false    | builds/tests                         |
| reports-site      | Generated Allure reports directory, to be pushed to the website repository at the `reports-site-path`.          | true     | reports-site                         |
| website-url       | Custom URL to use instead of the default GitHub Pages URL for the website where Allure report will be published | false  |                                      |
| report-name       | The name to be shown on top of the Overview tab in the Allure report                                            | false    | Allure Test Report                   |
| ci-name           | The name of the CI server                                                                                       | false    | GitHub Action: {{ github.workflow }} |
| max-reports       | Number of previous Allure reports to keep. Set to 0 to keep all reports.                                        | false    | 20                                   |

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