from __future__ import division
from time import sleep

from celery import Celery
from datetime import datetime, timedelta

from ..celery_dashboard import init
from ..celery_dashboard.utils import set_progress

celery_app = Celery('test_app', broker='redis://localhost', backend='redis://localhost')
celery_app.conf.update(accept_content=['json', 'pickle'],
                       CELERY_ACCEPT_CONTENT=['json', 'pickle'],  # celery 3
                       worker_prefetch_multiplier=1)


@celery_app.task(name="retry_with_countdown", bind=True)
def retry_with_countdown(self, countdown):
    self.retry(countdown=countdown)


@celery_app.task(name="retry_with_eta", bind=True)
def retry_with_eta(self, countdown):
    self.retry(eta=datetime.utcnow() + timedelta(countdown))


@celery_app.task(name="empty_task")
def empty_task(x):
    return x


@celery_app.task
def no_name(x):
    return 1


@celery_app.task(name="queue_no_name")
def queue_no_name():
    no_name.apply_async((my_arg,), queue="test_queue", serializer="pickle")


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


def my_arg():
    pass


beat_schedule = {
    "divide-1s": {
        'task': 'divide',
        'schedule': 1,
        'args': (20, 2),
        'options': {
            'queue': 'test_queue',
        }
    },
    "divide-fail": {
        'task': 'divide',
        'schedule': 1,
        'args': (20, 0),
        'options': {
            'queue': 'test_queue',
        }
    },
    "no-name": {
        'task': "queue_no_name",
        'schedule': 1,
        'args': [],
        'options': {
            'queue': 'test_queue',
            'serializer': 'pickle'
        }
    },
    "long-run": {
        'task': "long_running",
        'schedule': 4,
        'options': {
            'queue': 'test_queue',
        }
    },
    "retry_with_countdown": {
        'task': "retry_with_countdown",
        'schedule': 4,
        "kwargs": {"countdown": 10},
        'options': {
            'queue': 'test_queue',
        }
    }
}

celery_app.conf.CELERYBEAT_SCHEDULE = celery_app.conf.beat_schedule = beat_schedule

init(celery_app, "postgresql://docker:docker@localhost:5432/docker", "admin", "admin", db_echo="debug")
