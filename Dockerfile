FROM andgineer/allure:2.28.0

ENV PYTHON_SOURCE=/generate-allure-report
ENV PYTHONPATH="$PYTHON_SOURCE:$PYTHONPATH"

# Local-specific script to set up corporate proxy etc
ARG SSL_CERT_FILE
ENV SSL_CERT_FILE=$SSL_CERT_FILE
COPY .setup-scripts* /.setup-scripts
RUN /.setup-scripts/debian.sh || true

RUN uv pip install requests
WORKDIR /github/workspace

COPY src/ $PYTHON_SOURCE/app/

ENTRYPOINT python -m app.allure_generate
