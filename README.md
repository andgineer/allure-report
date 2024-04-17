# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andgineer/allure-report/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                        |    Stmts |     Miss |   Cover |   Missing |
|---------------------------- | -------: | -------: | ------: | --------: |
| src/\_\_about\_\_.py        |        1 |        0 |    100% |           |
| src/action\_base.py         |       18 |        0 |    100% |           |
| src/allure\_generate.py     |       84 |        5 |     94% |65, 78-80, 112 |
| src/github\_vars.py         |       89 |        0 |    100% |           |
| src/inputs\_outputs.py      |       79 |       17 |     78% |43, 50, 53, 77-83, 86, 89-90, 93, 96, 117, 124-125, 128, 131, 134 |
| src/templates/executor.json |        1 |        0 |    100% |           |
|                   **TOTAL** |  **272** |   **22** | **92%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/andgineer/allure-report/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/allure-report/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/andgineer/allure-report/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/andgineer/allure-report/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fandgineer%2Fallure-report%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/andgineer/allure-report/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.