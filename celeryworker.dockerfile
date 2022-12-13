FROM python:3.9

WORKDIR /app/

RUN apt-get update

# Need to curriculum-parser
RUN apt-get install -y ghostscript
RUN apt-get install -y libsm6 libxext6 libgl1-mesa-dev

ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.2.0 \
    POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$POETRY_HOME/bin:$PATH"

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

ENV C_FORCE_ROOT=1

COPY ./src /app
WORKDIR /app

ENV PYTHONPATH=/app

COPY ./src/worker-start.sh /worker-start.sh
RUN chmod +x /worker-start.sh

CMD ["bash", "/worker-start.sh"]
