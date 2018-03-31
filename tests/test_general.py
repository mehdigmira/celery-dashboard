import datetime
import pytest
import pytz
import time

from sqlalchemy import create_engine

from .utils import useless_function


@pytest.mark.parametrize(("queue", ), [("test_queue", ), (None, )])
@pytest.mark.parametrize(("countdown", ), [(10, ), (datetime.timedelta(seconds=10), )])
def test_queue_general(celery_worker, queue, countdown):
    from ..celery_dashboard.models import session_ctx_manager, Task
    from .celery_app import div

    apply_async_kwargs = {}
    if queue:
        apply_async_kwargs["queue"] = queue
    if countdown:
        if isinstance(countdown, int):
            apply_async_kwargs["countdown"] = countdown
        else:
            apply_async_kwargs["eta"] = countdown + datetime.datetime.utcnow()
    div.apply_async((20, 2), **apply_async_kwargs)

    with session_ctx_manager() as session:
        task = session.query(Task).one()
        assert task.status == "QUEUED"
        assert task.routing_key == queue if queue else "celery"
        assert task.name == "divide"
        assert task.args == '(20, 2)'
        assert task.kwargs == '{}'
        assert task.result is None
        assert task.meta is None
        assert task.exception_type is None
        assert task.traceback is None
        assert task.date_queued <= pytz.UTC.localize(datetime.datetime.utcnow())
        if countdown:
            if isinstance(countdown, int):
                assert task.eta <= pytz.UTC.localize(datetime.datetime.utcnow()) + datetime.timedelta(seconds=countdown)
            else:
                assert task.eta <= pytz.UTC.localize(datetime.datetime.utcnow()) + countdown
        assert task.date_done is None


def test_queue_with_pickle(celery_worker):
    from .celery_app import empty_task
    from ..celery_dashboard.models import session_ctx_manager, Task
    empty_task.apply_async((useless_function, ), serializer="pickle")
    with session_ctx_manager() as session:
        task = session.query(Task).one()
        assert task.status == "QUEUED"
        assert task.routing_key == "celery"
        assert task.name == "empty_task"
        assert "(<function " in task.args
        assert task.kwargs == '{}'
        assert task.result is None
        assert task.meta is None
        assert task.exception_type is None
        assert task.traceback is None
        assert task.date_queued <= pytz.UTC.localize(datetime.datetime.utcnow())


@pytest.mark.parametrize(("countdown", ), [ (None, )])
def test_successful_job(celery_worker, countdown):
    celery_worker.start()
    from ..celery_dashboard.models import session_ctx_manager, Task
    from .celery_app import div
    from .conf import PG_URI
    from ..celery_dashboard.models import SessionMaker
    from .utils import wait_for_task_to_run

    db_engine = create_engine(PG_URI, client_encoding='utf8', convert_unicode=True, echo='debug')
    SessionMaker.configure(bind=db_engine)

    if countdown:
        div.apply_async((20, 2), countdown=countdown)
        time.sleep(3)
    else:
        wait_for_task_to_run(div.apply_async((20, 2)))

    with session_ctx_manager() as session:
        for i in range(2):
            now = pytz.UTC.localize(datetime.datetime.utcnow())
            task = session.query(Task).one()
            if countdown is None or i == 1:
                print("MEHDI")
                assert task.status == "SUCCESS"
                assert task.routing_key == "celery"
                assert task.name == "divide"
                assert task.args == '(20, 2)'
                assert task.kwargs == '{}'
                assert task.result == '10.0'
                assert task.meta is None
                assert task.exception_type is None
                assert task.traceback is None
                assert task.date_queued <= now
                assert task.eta <= now
                assert task.date_done <= now
                break
            else:
                assert task.status == "QUEUED"
                assert task.routing_key == "celery"
                assert task.name == "divide"
                assert task.args == '(20, 2)'
                assert task.kwargs == '{}'
                assert task.result is None
                assert task.meta is None
                assert task.exception_type is None
                assert task.traceback is None
                assert task.date_queued <= now
                assert task.eta >= now
                assert task.date_done is None
                time.sleep(5)


def test_failing_job(celery_worker):
    celery_worker.start()
    from ..celery_dashboard.models import session_ctx_manager, Task
    from .celery_app import div
    from .utils import wait_for_task_to_run

    wait_for_task_to_run(div.apply_async((20, 0)))

    with session_ctx_manager() as session:
        now = pytz.UTC.localize(datetime.datetime.utcnow())
        task = session.query(Task).one()
        assert task.status == "FAILURE"
        assert task.routing_key == "celery"
        assert task.name == "divide"
        assert task.args == '(20, 0)'
        assert task.kwargs == '{}'
        assert task.result is None
        assert task.meta is None
        assert task.exception_type == 'ZeroDivisionError'
        assert 'ZeroDivisionError: division by zero' in task.traceback
        assert task.date_queued <= now
        assert task.eta <= now
        assert task.date_done <= now

@pytest.mark.parametrize(("task_arg", "case"), [(useless_function, 0), ({"x": 1}, 1)])
def test_successful_job_with_pickle(celery_worker_no_backend, task_arg, case):
    celery_worker_no_backend.start()
    from .celery_app_no_backend import empty_task
    from ..celery_dashboard.models import session_ctx_manager, Task
    from .utils import wait_for_task_to_run

    wait_for_task_to_run(empty_task.apply_async((task_arg, ), serializer="pickle"))
    with session_ctx_manager() as session:
        task = session.query(Task).one()
        assert task.status == "SUCCESS"
        assert task.routing_key == "celery"
        assert task.name == "empty_task"
        if case == 0:
            assert "(<function " in task.args
            assert "<function useless_function" in task.result
        else:
            assert task.args == "({'x': 1},)"
            assert task.result == '{"x": 1}'
        assert task.kwargs == '{}'
        assert task.meta is None
        assert task.exception_type is None
        assert task.traceback is None
        assert task.date_queued <= pytz.UTC.localize(datetime.datetime.utcnow())

@pytest.mark.parametrize(("with_eta", ), [(True, ), (False, )])
def test_retry_job(celery_worker, with_eta):
    celery_worker.start()
    from .celery_app import retry_with_countdown, retry_with_eta
    from ..celery_dashboard.models import session_ctx_manager, Task
    from .utils import wait_for_task_to_run
    if with_eta:
        retry_task = retry_with_eta
    else:
        retry_task = retry_with_countdown
    wait_for_task_to_run(retry_task.apply_async(kwargs={"countdown": 5}))
    with session_ctx_manager() as session:
        task = session.query(Task).one()
        assert task.status == "RETRY"
        assert task.routing_key == "celery"
        assert task.args == "()"
        assert task.result is None
        assert task.kwargs == "{'countdown': 5}"
        assert task.meta is None
        assert "Retry" in task.exception_type
        assert '/app/tests/celery_app.py' in task.traceback
        assert task.date_queued <= pytz.UTC.localize(datetime.datetime.utcnow())