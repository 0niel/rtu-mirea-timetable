FROM tiangolo/uvicorn-gunicorn-fastapi:latest

WORKDIR /app/

RUN apt-get update && apt-get install -y libgl1-mesa-dev

ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.2.0 \
    POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -


ENV PATH="$PATH:$POETRY_HOME/bin"

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./src/pyproject.toml ./src/poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"

COPY ./src /app

COPY ./src/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

ENV PYTHONPATH=/app
