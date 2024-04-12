FROM andgineer/allure:2.27.0

ENV APP_HOME=app
ENV PYTHONPATH=/$APP_HOME

COPY src/ /$APP_HOME/
COPY templates/ /templates/

ENTRYPOINT python3 -m $APP_HOME.allure_generate
