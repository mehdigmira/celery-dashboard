import datetime
import pytest
import pytz
import time

from .utils import useless_function, wait_for_task_to_run


@pytest.mark.parametrize(("queue", ), [("test_queue", ), (None, )])
@pytest.mark.parametrize(("countdown", ), [(10, ), (datetime.timedelta(seconds=10), )])
def test_queue_general(celery_worker, queue, countdown):
    from .conf import PG_URI
    from ..celery_dashboard.models import SessionManager, session_cleanup, Task
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

    session = SessionManager().session_factory(dburi=PG_URI)
    with session_cleanup(session):
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

        session.commit()


def test_queue_with_pickle(celery_worker):
    from .celery_app import empty_task
    from .conf import PG_URI
    from ..celery_dashboard.models import SessionManager, session_cleanup, Task
    empty_task.apply_async((useless_function, ), serializer="pickle")
    session = SessionManager().session_factory(dburi=PG_URI)
    with session_cleanup(session):
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


@pytest.mark.parametrize(("countdown", ), [(5, ), (None, )])
def test_successful_job(celery_worker, countdown):
    celery_worker.start()
    from .conf import PG_URI
    from ..celery_dashboard.models import SessionManager, session_cleanup, Task
    from .celery_app import div

    if countdown:
        div.apply_async((20, 2), countdown=countdown)
        time.sleep(3)
    else:
        div.apply_async((20, 2))
        wait_for_task_to_run()

    session = SessionManager().session_factory(dburi=PG_URI)
    with session_cleanup(session):
        for i in range(2):
            now = pytz.UTC.localize(datetime.datetime.utcnow())
            task = session.query(Task).one()
            if countdown is None or i == 1:
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

            session.commit()


def test_failing_job(celery_worker):
    celery_worker.start()
    from .conf import PG_URI
    from ..celery_dashboard.models import SessionManager, session_cleanup, Task
    from .celery_app import div

    div.apply_async((20, 0))

    wait_for_task_to_run()

    session = SessionManager().session_factory(dburi=PG_URI)
    with session_cleanup(session):
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

        session.commit()


@pytest.mark.parametrize(("task_arg", "case"), [(useless_function, 0), ({"x": 1}, 1)])
def test_successful_job_with_pickle(celery_worker, task_arg, case):
    celery_worker.start()
    from .celery_app import empty_task
    from .conf import PG_URI
    from ..celery_dashboard.models import SessionManager, session_cleanup, Task
    empty_task.apply_async((task_arg, ), serializer="pickle")
    wait_for_task_to_run()
    session = SessionManager().session_factory(dburi=PG_URI)
    with session_cleanup(session):
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
    from .conf import PG_URI
    from ..celery_dashboard.models import SessionManager, session_cleanup, Task
    if with_eta:
        retry_task = retry_with_eta
    else:
        retry_task = retry_with_countdown
    retry_task.apply_async(kwargs={"countdown": 5})
    wait_for_task_to_run()
    session = SessionManager().session_factory(dburi=PG_URI, echo=True)
    with session_cleanup(session):
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