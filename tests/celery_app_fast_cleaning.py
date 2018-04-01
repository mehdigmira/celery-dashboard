from time import sleep

from celery import Celery
from datetime import datetime, timedelta

from ..celery_dashboard import init
from ..celery_dashboard.utils import set_progress

celery_app = Celery('test_app', broker='redis://localhost', backend='redis://localhost')
celery_app.conf.update(accept_content=['json', 'pickle'], worker_prefetch_multiplier=1)

init(celery_app, "postgresql://docker:docker@localhost:5432/docker", db_echo="debug",
     cleaning_thresholds={"SUCCESS": 5})


@celery_app.task(name="retry_with_countdown", bind=True)
def retry_with_countdown(self, countdown):
    self.retry(countdown=countdown)


@celery_app.task(name="retry_with_eta", bind=True)
def retry_with_eta(self, countdown):
    self.retry(eta=datetime.utcnow() + timedelta(countdown))


@celery_app.task(name="empty_task")
def empty_task(x):
    return x


@celery_app.task(name="divide")
def div(x, y):
    return x / y


@celery_app.task(name="fast_divide", only_store=["FAILURE"])
def fast_div(x, y):
    return x / y


@celery_app.task(name="long_running", bind=True)
def long_running(self):
    for x in range(5):
        set_progress(self, x * 25)
        sleep(1)
