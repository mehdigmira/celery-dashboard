import time
from redis import StrictRedis


def wait_for_task_to_run(queue="celery"):
    redis_instance = StrictRedis()
    while True:
        if redis_instance.llen(queue) == 0:
            return
        time.sleep(0.5)


def useless_function():
    pass