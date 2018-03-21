from celery_dashboard.cleaning import dashboard_cleaning
from celery_dashboard.models import SessionManager
from celery_dashboard.signals import *


def init(celery_app, pg_db_uri, cleaning_thresholds=None):
    if not cleaning_thresholds:
        cleaning_thresholds = {}
    if "STARTED" not in cleaning_thresholds:
        cleaning_thresholds["STARTED"] = 3600
    if "SUCCESS" not in cleaning_thresholds:
        cleaning_thresholds["SUCCESS"] = 3600 * 4
    celery_app.conf.dashboard_pg_uri = pg_db_uri
    session_manager = SessionManager()
    engine = session_manager.get_engine(pg_db_uri)
    session_manager.prepare_models(engine)
    celery_app.task(name="dashboard_cleaning")(dashboard_cleaning)
    for status, threshold in cleaning_thresholds.items():
      celery_app.conf.beat_schedule['clean-%s-tasks' % status.lower()] = {
          'task': 'dashboard_cleaning',
          'schedule': threshold,
          'args': (status, threshold),
          'options': {
              'queue': 'celery_dashboard',
              'expires': 10 * 60
          }
      }