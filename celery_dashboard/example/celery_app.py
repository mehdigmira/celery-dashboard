from celery import Celery
from datetime import timedelta

from celery_dashboard import init
from celery_dashboard.signals import *

celery_app = Celery('tasks', broker='redis://localhost')
celery_app.conf.dashboard_redis_url = 'redis://localhost'

# celery_app.control.enable_events()

init(celery_app, "")


# @celery_app.task(name="div", only_store=("FAILURE",))
@celery_app.task(name="retry_with_cd", bind=True)
def div(self, x, y):
  self.retry(countdown=3600)
  return

@celery_app.task(name="success", bind=True)
def div(self, x, y):
  return x / y

# for y in range(100):
div.apply_async(kwargs={"x": 501, "y": 1})

