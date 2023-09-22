from __future__ import absolute_import

from celery import Celery
from celery.signals import worker_process_init
from opentelemetry.instrumentation.celery import CeleryInstrumentor

from app.config import config


@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    CeleryInstrumentor().instrument()


app = Celery("worker.tasks", broker=config.BROKER_URL, include=["worker.tasks"])

app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])
app.conf.timezone = "UTC"

if __name__ == "__main__":
    app.start()
