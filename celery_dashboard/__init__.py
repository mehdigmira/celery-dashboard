from celery_dashboard.models import SessionManager
from celery_dashboard.signals import *


def init(celery_app, pg_db_uri):
  celery_app.conf.dashboard_pg_uri = pg_db_uri
  session_manager = SessionManager()
  engine = session_manager.get_engine(pg_db_uri)
  session_manager.prepare_models(engine)
