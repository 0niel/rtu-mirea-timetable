from __future__ import absolute_import

from celery import Celery

from app.config import config

app = Celery("worker.tasks", broker=config.BROKER_URL, include=["worker.tasks"])

app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])
app.conf.timezone = "UTC"

if __name__ == "__main__":
    app.start()
