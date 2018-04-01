from .models import Task


def set_progress(task, progress):
    request = task.request
    Task.upsert(request.id, status="STARTED", name=task.name, args=request.argsrepr, kwargs=request.kwargsrepr,
                routing_key=request.delivery_info["routing_key"], meta={"progress": progress})
