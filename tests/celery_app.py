from time import sleep

from celery import Celery
from datetime import datetime, timedelta

from ..celery_dashboard import init
from ..celery_dashboard.utils import set_progress

celery_app = Celery('test_app', broker='redis://localhost')
celery_app.conf.update(accept_content = ['json', 'pickle'])

init(celery_app, "postgresql://docker:docker@localhost:5432/docker")


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


@celery_app.task(name="long_running")
def long_running(self):
    for x in range(100):
        sleep(1)
        set_progress(self, x + 1)
