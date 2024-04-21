FROM andgineer/allure:2.28.0

ENV PYTHON_SOURCE=/generate-allure-report
ENV PYTHONPATH="$PYTHON_SOURCE:$PYTHONPATH"

WORKDIR /github/workspace

COPY src/ $PYTHON_SOURCE/app/

ENTRYPOINT python -m app.allure_generate
