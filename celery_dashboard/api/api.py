import json

from flask import Blueprint, abort
from flask import current_app
from flask import request
from sqlalchemy import func

from ..auth import requires_auth
from ..models import Task
from ..utils import cancel_tasks, requeue_tasks

api = Blueprint('api', __name__, url_prefix='/api')


def with_task(func):
    def decorator(task_id, *args, **kwargs):
        task = current_app.db.session.query(Task).filter(Task.task_id == task_id).one()
        return func(task, *args, **kwargs)

    decorator.__name__ = func.__name__
    return decorator


@api.route("/tasks", methods=["GET", "DELETE", "POST"])
@requires_auth
def tasks():
    q = current_app.db.session.query(Task)

    if request.method == "GET":
        data = request.args
    else:
        data = request.get_json()

    if "status" in data:
        q = q.filter(Task.status == data["status"])

    if "queue" in data:
        q = q.filter(Task.routing_key == data["queue"])

    if "task" in data:
        q = q.filter(Task.name == data["task"])

    if "exception" in data:
        q = q.filter(Task.exception_type == data["exception"])

    if "taskId" in data:
        q = q.filter(Task.task_id == data["taskId"])

    if request.method == "GET":
        count = q.count()
        # add sorting here
        sorts = data.get("sort") or ""
        if sorts:
            for sort_str in sorts.split(","):
                col, direction = sort_str.split(":")
                q = q.order_by(getattr(getattr(Task, col), direction)())

        # offset and limit
        offset = int(request.args.get("start") or 0)
        limit = int(request.args.get("end") or 5) - offset
        q = q.order_by(Task.date_queued.asc()).offset(offset).limit(limit)

        result = [task.serialized for task in q.yield_per(1000)]

        return json.dumps({"result": result, "count": count})
    elif request.method == "DELETE":
        count = cancel_tasks(q.yield_per(1000), current_app.db.session)
        current_app.db.session.commit()
        return json.dumps({"count": count})
    elif request.method == "POST":
        task_ids = requeue_tasks(q.yield_per(1000), current_app.db.session)
        current_app.db.session.commit()
        return json.dumps({"count": len(task_ids)})


@api.route("/task/<task_id>/revoke")
@requires_auth
@with_task
def revoke_task(task):
    cancel_tasks([task], current_app.db.session)
    current_app.db.session.commit()

    return json.dumps({"message": "ok"})


@api.route("/task/<task_id>/requeue")
@requires_auth
@with_task
def requeue_task(task):
    task_ids = requeue_tasks([task], current_app.db.session)
    if not task_ids:
        abort(400)
    current_app.db.session.commit()

    return json.dumps({"taskId": task_ids[0]})


@api.route("/queues")
@requires_auth
def get_queues():
    by_queue = {}

    q = (current_app.db.session.query(Task.status, Task.routing_key, func.count(Task.id))
         .filter(Task.status.in_(["QUEUED", "STARTED", "RETRY"]))
         .group_by(Task.status, Task.routing_key))

    for row in q:
        status, routing_key, count = row
        sub_dict = by_queue.setdefault(routing_key, {"QUEUED": 0, "STARTED": 0, "RETRY": 0, "ALL": 0,
                                                     "routing_key": routing_key})
        sub_dict[status] = count
        sub_dict["ALL"] += count

    return json.dumps({"result": list(by_queue.values())})


@api.route("/workers")
@requires_auth
def get_workers():
    workers = []
    for worker_name, stats in (current_app.celery_app.control.inspect().stats() or {}).items():
        workers.append({
            "name": worker_name,
            "broker": stats.get("broker", {}).get("transport"),
            "poolSize": stats.get("pool", {}).get("max-concurrency"),
            "tasks": stats.get("total", {}),
            "pid": stats.get("pid")
        })
    return json.dumps({"result": workers})


@api.route("/task", methods=["POST"])
@requires_auth
def create_task():
    data = request.get_json()
    task_id = current_app.celery_app.send_task(data["task"], kwargs=data["kwargs"], queue=data["queue"] or "celery")
    return json.dumps({"taskId": str(task_id)})