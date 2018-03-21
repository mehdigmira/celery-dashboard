from celery_dashboard.models import Task


def set_progress(task, progress):
  request = task.request
  Task.upsert(request.id, status="STARTED", name=task.name, args=request.args, kwargs=request.kwargs,
              routing_key=request.delivery_info["routing_key"], meta={"progress": progress})
