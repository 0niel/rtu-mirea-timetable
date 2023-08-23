FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app/

COPY . /app

RUN pip install -r requirements.txt

EXPOSE $PORT

ENV PORT="${PORT:-8080}"
ENV APP_MODULE="app.main:app"
