FROM andgineer/allure:2.27.0

ENV PYTHON_SOURCE=/generate-allure-report
ENV PYTHONPATH=$PYTHON_SOURCE

WORKDIR /github/workspace

COPY src/ $PYTHON_SOURCE/app/

ENTRYPOINT python3 -m app.allure_generate
