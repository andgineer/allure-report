FROM andgineer/allure:2.27.0

ENV PYTHONPATH=/github/workspace/src

WORKDIR /github/workspace

ENTRYPOINT python3 -m src.allure_generate
