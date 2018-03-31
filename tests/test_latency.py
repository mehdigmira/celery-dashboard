import threading
from datetime import datetime
import time
import pytz
from celery.signals import before_task_publish

def test_publisher_latency(celery_worker):
    celery_worker.start()

    from .celery_app import div
    from ..celery_dashboard.models import session_ctx_manager, Task
    from ..celery_dashboard.signals import task_sent_handler
    from .utils import wait_for_task_to_run

    before_task_publish.receivers = []
    cache = []

    @before_task_publish.connect
    def before_task_receiver_with_latency(*args, **kwargs):
        cache.extend([args, kwargs])

    wait_for_task_to_run(div.apply_async((20, 2)))

    with session_ctx_manager() as session:
        task = session.query(Task).one()
        assert task.status == "SUCCESS"
        assert task.routing_key == "celery"
        assert task.args == "(20, 2)"
        assert task.result == "10.0"
        assert task.kwargs == "{}"
        assert task.meta is None
        assert task.exception_type is None
        assert task.traceback is None
        assert task.date_queued is None
        assert task.date_done <= pytz.UTC.localize(datetime.utcnow())

        task_sent_handler(*cache[0], **cache[1])

        session.expire(task)
        session.refresh(task)

        assert task.status == "SUCCESS"
        assert task.date_queued <= pytz.UTC.localize(datetime.utcnow())
