import json

import requests
import pytest
import time


def assert_task(tasks, task_id, assert_dict):
    task = next(task for task in tasks if task["task_id"] == task_id)
    for k, v in assert_dict.items():
        assert task[k] == v


@pytest.mark.parametrize(("action", ), [("cancel",), ("requeue",)])
@pytest.mark.parametrize(("filters", "expected_count"),
                         [({"status": "QUEUED"}, 2), ({"queue": "test_queue"}, 1), ({"task": "divide"}, 4),
                          ({"taskId": lambda wait_for: wait_for[0].task_id}, 1),
                          ({"exception": "ZeroDivisionError"}, 1)])
def test_filtered_tasks(celery_worker, api, action, filters, expected_count):
    from .celery_app import div, retry_with_countdown
    from .utils import wait_for_task_to_run

    api.start()
    celery_worker.start()

    wait_for = [div.apply_async((20, 2)), div.apply_async((20, 0)), retry_with_countdown.apply_async((10,))]
    do_not_wait_for = [div.apply_async((20, 2), countdown=10), div.apply_async((20, 2), queue="test_queue")]

    for async_res in wait_for:
        wait_for_task_to_run(async_res)

    all_tasks = requests.get(api.api_url + "tasks").json()

    assert all_tasks["count"] == 5
    assert_task(all_tasks["result"], wait_for[0].task_id, {
        "routing_key": "celery",
        "status": "SUCCESS",
        "result": "10.0",
        "name": "divide"
    })
    assert_task(all_tasks["result"], wait_for[1].task_id, {
        "routing_key": "celery",
        "status": "FAILURE",
        "result": None,
        "name": "divide"
    })
    assert_task(all_tasks["result"], wait_for[2].task_id, {
        "routing_key": "celery",
        "status": "RETRY",
        "result": None,
        "name": "retry_with_countdown"
    })

    assert_task(all_tasks["result"], do_not_wait_for[0].task_id, {
        "routing_key": "celery",
        "status": "QUEUED",
        "result": None,
        "name": "divide"
    })
    assert_task(all_tasks["result"], do_not_wait_for[1].task_id, {
        "routing_key": "test_queue",
        "status": "QUEUED",
        "result": None,
        "name": "divide"
    })

    celery_worker.stop()

    filters_to_request = dict(filters)
    if "taskId" in filters:
        filters_to_request = {"taskId": filters["taskId"](wait_for)}

    route = api.api_url + "tasks?%s=%s" % (filters_to_request.keys()[0], filters_to_request.values()[0])
    tasks = requests.get(route).json()
    assert tasks["count"] == expected_count
    if action == "cancel":
        requests.delete(api.api_url + "tasks", data=json.dumps(filters_to_request),
                        headers={'content-type': 'application/json'})
        tasks = requests.get(route).json()
        if "task" in filters:
            assert tasks["count"] == 2
        elif "status" not in filters and "queue" not in filters:
            assert tasks["count"] == 0
    else:
        requests.post(api.api_url + "tasks", data=json.dumps(filters_to_request),
                      headers={'content-type': 'application/json'})
        tasks = requests.get(route).json()
        if "taskId" in filters:
            assert tasks["count"] == 0
            assert requests.get(api.api_url + "tasks?status=QUEUED").json()["count"] == 2 + expected_count
        elif "exception" in filters:
            assert tasks["count"] == 0
            assert requests.get(api.api_url + "tasks?status=QUEUED").json()["count"] == 2 + expected_count
        else:
            assert tasks["count"] == expected_count
            for task in tasks["result"]:
                assert task["status"] == "QUEUED"


def test_revoke_task(api, celery_worker):
    from .celery_app import div
    from ..celery_dashboard.models import session_ctx_manager, Task
    from .utils import wait_for_task_to_run

    api.start()
    celery_worker.start()

    # queue task
    async_res = div.apply_async((20, 2), countdown=5)
    time.sleep(2)

    # revoke it
    requests.get(api.api_url + "task/%s/revoke" % async_res.task_id)

    # sleep until it is discarded by worker
    time.sleep(5)

    with session_ctx_manager() as session:
        task = session.query(Task).one()
        assert task.status == "REVOKED"

        # run this now
        async_res = wait_for_task_to_run(div.apply_async((20, 0)))

        task = session.query(Task).filter(Task.task_id == async_res.task_id).one()
        assert task

        # task is not queued it should just be deleted from db
        requests.get(api.api_url + "task/%s/revoke" % async_res.task_id)
        task = session.query(Task).filter(Task.task_id == async_res.task_id).first()
        assert task is None


def test_requeue_task(api_no_backend, celery_worker_no_backend):
    from .celery_app import div, empty_task
    from ..celery_dashboard.models import session_ctx_manager, Task
    from .utils import wait_for_task_to_run, useless_function

    api_no_backend.start()
    celery_worker_no_backend.start()

    divide_job = wait_for_task_to_run(div.apply_async((20, 2)))
    empty_job = wait_for_task_to_run(empty_task.apply_async((useless_function,), serializer="pickle"))

    celery_worker_no_backend.stop()

    requests.get(api_no_backend.api_url + "task/%s/requeue" % divide_job.task_id)
    requests.get(api_no_backend.api_url + "task/%s/requeue" % empty_job.task_id)

    with session_ctx_manager() as session:
        tasks = session.query(Task).all()
        for task in tasks:
            if task.name == "divide":
                assert task.status == "QUEUED"
            else:  # here we won't be able to load args, so it won't be requeued
                assert task.status == "SUCCESS"
