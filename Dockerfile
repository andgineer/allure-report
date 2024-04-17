FROM andgineer/allure:2.27.0

ENV PYTHON_SOURCE=/generate-allure-report
ENV PYTHONPATH="$PYTHON_SOURCE:$PYTHONPATH"

WORKDIR /github/workspace

COPY src/ $PYTHON_SOURCE/app/
COPY requirements.txt $PYTHON_SOURCE/

# Create a virtual environment in the container
#RUN python3 -m venv /opt/venv

# Activate the virtual environment
#ENV PATH="/opt/venv/bin:$PATH"

# Install requirements using pip from the virtual environment
#RUN pip install --no-cache-dir -r $PYTHON_SOURCE/requirements.txt

ENTRYPOINT python3 -m app.allure_generate
