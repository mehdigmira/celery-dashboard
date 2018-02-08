from datetime import datetime

import dateutil.parser
from celery import current_app
from celery.signals import before_task_publish, task_prerun, task_retry, task_success, task_failure

from celery_dashboard.models import Task


def check_restricted_statuses(status, task_name_getter):
  def decorator(receiver):
    def wrapper(sender=None, **kwargs):
      if hasattr(current_app.tasks[task_name_getter(sender)], "only_store"):
        if status not in current_app.tasks[task_name_getter(sender)].only_store:
          return
      else:
        return receiver(sender, **kwargs)
    return wrapper
  return decorator


@before_task_publish.connect
@check_restricted_statuses(status="QUEUED", task_name_getter=lambda x: x)
def task_sent_handler(sender=None, headers=None, body=None, properties=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    info = headers if 'task' in headers else body
    now = datetime.utcnow()
    eta = info.get("eta") or now
    Task.upsert(info["id"], status="QUEUED", date_queued=now, name=sender,
                routing_key=kwargs.get("routing_key"),
                args=info.get("args", []), kwargs=info.get("kwargs", {}), on_conflict_do_nothing=True, eta=eta)


@task_prerun.connect
@check_restricted_statuses(status="STARTED", task_name_getter=lambda x: x.name)
def task_started_handler(sender=None, task_id=None, args=None, kwargs=None, **opts):
  Task.upsert(task_id, status="STARTED", name=sender.name, args=args, kwargs=kwargs,
              routing_key=sender.request.delivery_info["routing_key"])


@task_retry.connect
@check_restricted_statuses(status="RETRY", task_name_getter=lambda x: x.name)
def task_retry_handler(sender=None, reason=None, request=None, einfo=None, **opts):
  eta = getattr(sender.request, "eta", None)
  update_dict = {}
  if eta:
    update_dict["eta"] = dateutil.parser.parse(eta)
  Task.upsert(request.id, status="RETRY", name=sender.name, routing_key=request.delivery_info["routing_key"],
              exception_type=str(reason), args=request.args, kwargs=request.kwargs, traceback=str(einfo),
              date_done=datetime.utcnow(), **update_dict)


@task_success.connect
@check_restricted_statuses(status="SUCCESS", task_name_getter=lambda x: x.name)
def task_success_handler(sender=None, result=None, **opts):
  Task.upsert(sender.request.id, status="SUCCESS", name=sender.name,
              routing_key=sender.request.delivery_info["routing_key"],
              result=result, args=sender.request.args, kwargs=sender.request.kwargs, date_done=datetime.utcnow())


@task_failure.connect
@check_restricted_statuses(status="FAILURE", task_name_getter=lambda x: x.name)
def task_failure_handler(sender=None, exception=None, einfo=None, **opts):
  Task.upsert(sender.request.id, status="FAILURE", name=sender.name,
              routing_key=sender.request.delivery_info["routing_key"],
              exception_type=einfo.type.__name__, traceback=str(einfo.traceback), args=sender.request.args,
              kwargs=sender.request.kwargs,
              date_done=datetime.utcnow())
