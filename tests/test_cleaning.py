import time


def test_cleaning(celery_worker_fast_cleaning):
    from .celery_app import div
    from ..celery_dashboard.models import session_ctx_manager, Task

    celery_worker_fast_cleaning.start(beat=True, queue="celery_dashboard,celery")

    div.apply_async((20, 2))
    div.apply_async((20, 0))

    time.sleep(3)

    with session_ctx_manager() as session:
        tasks = session.query(Task).filter(Task.name == "divide").all()
        assert len(tasks) == 2
        assert set([task.status for task in tasks]) == {"SUCCESS", "FAILURE"}

    time.sleep(10)

    with session_ctx_manager() as session:
        tasks = session.query(Task).filter(Task.name == "divide").all()
        assert len(tasks) == 1
        assert set([task.status for task in tasks]) == {"FAILURE"}
