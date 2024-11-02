FROM andgineer/allure:2.32.0

ENV PYTHON_SOURCE=/generate-allure-report
ENV APP_HOME=$PYTHON_SOURCE/app
ENV PYTHONPATH="$PYTHON_SOURCE:$APP_HOME:$PYTHONPATH"

# Local-specific script to set up corporate proxy etc
ARG SSL_CERT_FILE
ENV SSL_CERT_FILE=$SSL_CERT_FILE
COPY .setup-scripts* /.setup-scripts
RUN /.setup-scripts/debian.sh || true

RUN uv pip install requests
WORKDIR /github/workspace

COPY src/ $APP_HOME

ENTRYPOINT python -m app.allure_generate
