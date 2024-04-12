# GitHub Action to generate Allure Report

A GitHub Action that generates a visually stunning Allure test report.

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
