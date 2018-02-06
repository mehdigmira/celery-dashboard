import json

from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import request

from celery_dashboard.models import Task

api = Blueprint('api', __name__, url_prefix='/api')


@api.route("/tasks")
def get_tasks():
  data = request.args

  offset = int(request.args.get("start") or 0)
  limit = int(request.args.get("end") or 5) - offset

  q = current_app.db.session.query(Task)

  if "status" in data:
    q = q.filter(Task.status == data["status"])

  if "queue" in data:
    q = q.filter(Task.routing_key == data["queue"])

  if "task_name" in data:
    q = q.filter(Task.name == data["task_name"])

  if "exception_type" in data:
    q = q.filter(Task.exception_type == data["exception_type"])

  count = q.count()
  q = q.order_by(Task.date_queued.asc()).offset(offset).limit(limit)
  result = [task.serialized for task in q.yield_per(1000)]

  return json.dumps({"result": result, "count": count})


@api.route("/task/<task_id>/revoke")
def revoque_task(task_id):
  current_app.celery_app.revoque(task_id)

  return json.dumps({"message": "ok"})


@api.route("/task/<task_id>/requeue")
def requeue_task(task_id):
  task = current_app.db.session.query(Task).filter(Task.task_id == task_id)

  current_app.celery_app.apply_async(task.name, args=task.args or [], kwds=task.kwargs or {},
                                     queue=task.routing_key or "celery")

  return json.dumps({"message": "ok"})


@api.route("/task/<task_id>/forget")
def forget_task(task_id):
  current_app.db.session.query(Task).filter(Task.task_id == task_id).delete()

  return json.dumps({"message": "ok"})

