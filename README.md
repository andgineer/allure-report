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
    - name: Checkout gh-pages with previous Allure reports
      uses: actions/checkout@v4
      with:
        ref: gh-pages
        path: gh-pages
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

`report-path` is where our report located in the website. 
We use that path to get previous report from `website-source`, and to create redirect from the root
to the last report.

As a result of the action we will have in folder `allure-report` new Allure report as well as previous 
(up to `max-reports`).

```yaml
    - name: Generate Allure test report
      uses: andgineer/allure-report@main
      with:
        website-source: gh-pages
        allure-results: allure-results
        allure-report: allure-report
        max-reports: 100
        report-path: allure
```

To publish the report on the github pages you can use whatever action you like.
For example:

```yaml
    - name: Publish Allure test report
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_branch: gh-pages
        publish_dir: allure-report
        destination_dir: allure
```

See full example in
[the workflow](https://github.com/andgineer/bitwarden-import-msecure/blob/main/.github/workflows/ci.yml)

## Inputs

| Name               | Description                                                                                               | Required | Default        |
|--------------------|-----------------------------------------------------------------------------------------------------------|----------|----------------|
| allure-results     | Allure test result directory created by tests.                                                            | true     | allure-results |
| website-source     | Website checkout location (e.g., from the gh-pages branch).                                               | true     | gh-pages       |
| report-path        | Allure report path within the website.                                                                    | false    | test-report    |
| allure-report      | Generated Allure report directory, to be pushed to the website repository at the `report-path`.           | true     | allure-report  |
| website-url        | Custom URL to use instead of the default GitHub Pages URL for the website where Allure report will be published | false  |                |
| report-name        | The name to be shown on top of the Overview tab in the Allure report                                      | false    | Allure Test Report |
| ci-name            | The name of the CI server                                                                                 | false    | GitHub Action: {{ github.workflow }} |
| max-reports| Number of previous Allure reports to keep. Set to 0 to keep all reports.                                  | false    | 20             |

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