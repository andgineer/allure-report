FROM andgineer/allure:2.27.0

ARG APP_HOME=/app

WORKDIR $APP_HOME
ENTRYPOINT ["python3", "allure_generate.py"]
