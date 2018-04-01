from multiprocessing.util import register_after_fork

from sqlalchemy import create_engine

from .cleaning import dashboard_cleaning
from .models import SessionMaker, prepare_models
from .signals import *


def init(celery_app, pg_db_uri, cleaning_thresholds=None, db_echo=False):
    # setup db
    db_engine = create_engine(pg_db_uri, client_encoding='utf8', convert_unicode=True, echo=db_echo)
    SessionMaker.configure(bind=db_engine)
    prepare_models(db_engine)
    register_after_fork(db_engine, lambda engine: engine.dispose())

    # cleaning
    if not cleaning_thresholds:
        cleaning_thresholds = {}
    if "STARTED" not in cleaning_thresholds:
        cleaning_thresholds["STARTED"] = 3600
    if "SUCCESS" not in cleaning_thresholds:
        cleaning_thresholds["SUCCESS"] = 3600 * 4
    celery_app.conf.dashboard_pg_uri = pg_db_uri
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
