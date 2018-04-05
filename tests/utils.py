import time

from celery.backends.base import DisabledBackend
from redis import StrictRedis


def wait_for_task_to_run(task, queue="celery"):
    if isinstance(task.backend, DisabledBackend):
        redis_instance = StrictRedis()
        while True:
            if redis_instance.llen(queue) == 0:
                break
            time.sleep(0.5)
        time.sleep(0.5)
    else:
        try:
            task.wait(timeout=5)
        except Exception:
            pass
        time.sleep(0.5)


def useless_function():
    pass