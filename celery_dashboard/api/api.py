import json

from flask import Blueprint
from flask import current_app
from flask import request
from sqlalchemy import func

from ..models import Task

api = Blueprint('api', __name__, url_prefix='/api')


def with_task(func):
    def decorator(task_id, *args, **kwargs):
        task = current_app.db.session.query(Task).filter(Task.task_id == task_id).one()
        return func(task, *args, **kwargs)

    decorator.__name__ = func.__name__
    return decorator


@api.route("/tasks", methods=["GET", "DELETE", "POST"])
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

    count = q.count()

    if request.method == "GET":
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
        for task in q.yield_per(1000):
            current_app.celery_app.control.revoke(task.task_id)
        q.delete()
        current_app.db.session.commit()
        return json.dumps({"count": count})
    elif request.method == "POST":
        to_rm = []
        for task in q.yield_per(1000):
            to_rm.append(task.task_id)
            args = task.args or []
            kwargs = task.kwargs or {}
            try:
                if args:
                    if args.startswith("(") and args.endswith(")"):
                        args = "[" + args[1:-1] + "]"
                    args = json.loads(args)
                if kwargs:
                    kwargs = json.loads(kwargs)
            # args or kwargs were not jsonified, we do not requeue this kind of tasks
            # because that would imply pickling the arguments and it would be insecure
            except ValueError:
                continue
            current_app.celery_app.send_task(task.name, args=args, kwargs=kwargs, queue=task.routing_key or "celery")
            if len(to_rm) > 1000:
                current_app.db.session.query(Task).filter(Task.task_id.in_(to_rm)).delete(synchronize_session=False)
                to_rm = []
        if to_rm:
            current_app.db.session.query(Task).filter(Task.task_id.in_(to_rm)).delete(synchronize_session=False)
        current_app.db.session.commit()
        return json.dumps({"count": count})


@api.route("/task/<task_id>/revoke")
@with_task
def revoke_task(task):
    current_app.celery_app.control.revoke(task.task_id)
    current_app.db.session.delete(task)
    current_app.db.session.commit()

    return json.dumps({"message": "ok"})


@api.route("/task/<task_id>/requeue")
@with_task
def requeue_task(task):
    current_app.celery_app.send_task(task.name, args=task.args or [], kwargs=task.kwargs or {},
                                     queue=task.routing_key or "celery")
    current_app.db.session.delete(task)
    current_app.db.session.commit()

    return json.dumps({"message": "ok"})


@api.route("/queues")
def get_queues():
    by_queue = {}

    q = (current_app.db.session.query(Task.status, Task.routing_key, func.count(Task.id))
         .group_by(Task.status, Task.routing_key))

    for row in q:
        status, routing_key, count = row
        sub_dict = by_queue.setdefault(routing_key, {"QUEUED": 0, "STARTED": 0, "RETRY": 0, "ALL": 0,
                                                     "routing_key": routing_key})
        sub_dict[status] = count
        sub_dict["ALL"] += count

    return json.dumps({"result": by_queue.values()})


@api.route("/workers")
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
