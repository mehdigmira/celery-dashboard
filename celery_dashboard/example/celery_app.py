from celery import Celery

from celery_dashboard import init
from celery_dashboard.signals import *

celery_app = Celery('tasks', broker='redis://localhost')
celery_app.conf.dashboard_redis_url = 'redis://localhost'

# celery_app.control.enable_events()

init(celery_app, "")


# @celery_app.task(name="div", only_store=("FAILURE",))
@celery_app.task(name="div", bind=True)
def div(self, x, y):
  self.retry(countdown=10)
  return x / y

# for y in range(100):
div.apply_async(kwargs={"x": 501, "y": 1}, countdown=10)
