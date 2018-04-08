import json

from celery import current_app

from .models import Task


def set_progress(task, progress):
    request = task.request
    Task.upsert(request.id, status="STARTED", name=task.name, args=dump(request.args), kwargs=dump(request.kwargs),
                routing_key=request.delivery_info["routing_key"], meta={"progress": progress})


def dump(data):
    try:
        return json.dumps(data)
    except TypeError:
        return repr(data)


def load(args, kwargs):
    try:
        if args:
            if args.startswith("(") and args.endswith(")"):
                args = "[" + args[1:-1] + "]"
            args = json.loads(args)
        if kwargs:
            kwargs = json.loads(kwargs)
    # args or kwargs were not jsonified, we do not requeue this kind of tasks
    # because that would imply pickling the arguments and it would be insecure
    except (ValueError, TypeError):
        return
    return args, kwargs


def cancel_tasks(tasks, session):
    to_rm = []
    to_set_as_cancelled = []
    count = 0
    for task in tasks:
        count += 1
        if task.status == "QUEUED":
            current_app.control.revoke(task.task_id)
            to_set_as_cancelled.append(task.task_id)
        else:
            to_rm.append(task.task_id)
        if len(to_rm) > 1000:
            session.query(Task).filter(Task.task_id.in_(to_rm)).delete(synchronize_session=False)
            to_rm = []
        if len(to_set_as_cancelled) > 1000:
            (session.query(Task).filter(Task.task_id.in_(to_set_as_cancelled))
             .update({'status': "CANCELLED"}, synchronize_session=False))
            to_set_as_cancelled = []
    if to_rm:
        session.query(Task).filter(Task.task_id.in_(to_rm)).delete(synchronize_session=False)
    if to_set_as_cancelled:
        (session.query(Task).filter(Task.task_id.in_(to_set_as_cancelled))
         .update({'status': "CANCELLED"}, synchronize_session=False))
    return count


def requeue_tasks(tasks, session):
    to_rm = []
    task_ids = []
    for task in tasks:
        args = task.args or []
        kwargs = task.kwargs or {}
        loaded_data = load(args, kwargs)
        if not loaded_data:
            continue
        to_rm.append(task.task_id)
        args, kwargs = loaded_data
        task_ids.append(current_app.send_task(task.name,
                                              args=args, kwargs=kwargs, queue=task.routing_key or "celery").task_id)
        if len(to_rm) > 1000:
            session.query(Task).filter(Task.task_id.in_(to_rm)).delete(synchronize_session=False)
            to_rm = []
    if to_rm:
        session.query(Task).filter(Task.task_id.in_(to_rm)).delete(synchronize_session=False)
    return task_ids
