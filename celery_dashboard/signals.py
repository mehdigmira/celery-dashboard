from datetime import datetime, timedelta

import pytz
from celery import current_app
from celery.signals import before_task_publish, task_prerun, task_retry, task_success, task_failure, task_revoked

from .models import Task
from .utils import dump


def check_restricted_statuses(status, task_name_getter):
    def decorator(receiver):
        def wrapper(sender=None, **kwargs):
            if hasattr(current_app.tasks[task_name_getter(sender)], "only_store"):
                if status not in current_app.tasks[task_name_getter(sender)].only_store:
                    return
            return receiver(sender, **kwargs)

        return wrapper

    return decorator


@before_task_publish.connect
@check_restricted_statuses(status="QUEUED", task_name_getter=lambda x: x)
def task_sent_handler(sender=None, headers=None, body=None, properties=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    info = (headers if headers and 'task' in headers else body) or {}
    argsrepr = info.get("argsrepr") or dump(info["args"])
    kwargsrepr = info.get("kwargsrepr") or dump(info["kwargs"])
    now = pytz.UTC.localize(datetime.utcnow())
    eta = info.get("eta") or now
    Task.upsert(info["id"], status="QUEUED", date_queued=now, name=sender,
                routing_key=kwargs.get("routing_key"),
                args=argsrepr, kwargs=kwargsrepr, on_conflict_update={"date_queued": now}, eta=eta)


@task_prerun.connect
@check_restricted_statuses(status="STARTED", task_name_getter=lambda x: x.name)
def task_started_handler(sender=None, task_id=None, args=None, kwargs=None, **opts):
    now = pytz.UTC.localize(datetime.utcnow())
    Task.upsert(task_id, status="STARTED", name=sender.name, args=dump(sender.request.args),
                kwargs=dump(sender.request.kwargs), date_started=now,
                routing_key=sender.request.delivery_info["routing_key"])


@task_retry.connect
@check_restricted_statuses(status="RETRY", task_name_getter=lambda x: x.name)
def task_retry_handler(sender=None, reason=None, request=None, einfo=None, **opts):
    when = getattr(getattr(einfo, "exception", None), "when")
    eta = None
    if isinstance(when, datetime):
        eta = when
    elif isinstance(when, int):
        eta = pytz.UTC.localize(datetime.utcnow()) + timedelta(seconds=when)
    Task.upsert(request.id, status="RETRY", name=sender.name, routing_key=request.delivery_info["routing_key"],
                exception_type=str(reason), args=dump(sender.request.args), kwargs=dump(sender.request.kwargs),
                traceback=str(einfo),
                date_done=pytz.UTC.localize(datetime.utcnow()), eta=eta)


@task_success.connect
@check_restricted_statuses(status="SUCCESS", task_name_getter=lambda x: x.name)
def task_success_handler(sender=None, result=None, **opts):
    resultrepr = dump(result)
    Task.upsert(sender.request.id, status="SUCCESS", name=sender.name,
                routing_key=sender.request.delivery_info["routing_key"],
                result=resultrepr, args=dump(sender.request.args), kwargs=dump(sender.request.kwargs),
                date_done=pytz.UTC.localize(datetime.utcnow()))


@task_failure.connect
@check_restricted_statuses(status="FAILURE", task_name_getter=lambda x: x.name)
def task_failure_handler(sender=None, exception=None, einfo=None, **opts):
    Task.upsert(sender.request.id, status="FAILURE", name=sender.name,
                routing_key=sender.request.delivery_info["routing_key"],
                exception_type=einfo.type.__name__, traceback=str(einfo.traceback), args=dump(sender.request.args),
                kwargs=dump(sender.request.kwargs),
                date_done=pytz.UTC.localize(datetime.utcnow()))


@task_revoked.connect
@check_restricted_statuses(status="REVOKED", task_name_getter=lambda x: x.name)
def task_revoked_handler(sender=None, request=None, **opts):
    argsrepr = getattr(request, "argsrepr", None) or dump(request.args)
    kwargsrepr = getattr(request, "kwargsrepr", None) or dump(request.kwargs)
    Task.upsert(request.id, status="REVOKED", name=sender.name,
                routing_key=request.delivery_info["routing_key"],
                args=argsrepr, kwargs=kwargsrepr,
                date_done=pytz.UTC.localize(datetime.utcnow()))
