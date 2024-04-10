# GitHub Action to generate Allure Report

A GitHub Action that generates a visually stunning Allure test report.


## Inputs

| Name                   | Description                                                                        | Required | Default          |
|------------------------|------------------------------------------------------------------------------------|----------|------------------|
| allure-results         | Allure test result data directory                                                  | true     | allure-results   |
| allure-report          | Allure report directory                                                            | true     | allure-report    |
| site-source            | Directory where the website source files (e.g., from the gh-pages branch) are checked out | true     | site-source      |
| allure-history         | Allure report history directory stored in the site source directory                | true     | allure-history   |
| site-path              | Subdirectory within the site source directory where the Allure report will be published | false    |                  |
| number-reports-to-keep| Number of previous Allure reports to keep. Set to 0 to keep all reports            | false    | 20               |
| site-url               | Custom URL to use instead of the default GitHub Pages URL for the Allure report     | false    |                  |
