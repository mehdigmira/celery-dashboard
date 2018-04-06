from multiprocessing.util import register_after_fork

from sqlalchemy import create_engine

from .cleaning import dashboard_cleaning
from .models import SessionMaker, prepare_models


def init(celery_app, pg_db_uri, username=None, password=None, cleaning_thresholds=None, db_echo=False):
    # setup db
    db_engine = create_engine(pg_db_uri, client_encoding='utf8', convert_unicode=True, echo=db_echo)
    SessionMaker.configure(bind=db_engine)
    prepared = prepare_models(db_engine)
    if not prepared:
        return

    from .signals import task_sent_handler, task_started_handler, task_retry_handler, task_success_handler, \
        task_failure_handler, task_revoked_handler
    register_after_fork(db_engine, lambda engine: engine.dispose())

    # cleaning
    if not cleaning_thresholds:
        cleaning_thresholds = {}
    # if task hasn't finished after 3600s assume worker has been killed and couldn't send a signal
    if "STARTED" not in cleaning_thresholds:
        cleaning_thresholds["STARTED"] = 3600
    if "SUCCESS" not in cleaning_thresholds:
        cleaning_thresholds["SUCCESS"] = 3600 * 4
    celery_app.conf.dashboard_pg_uri = pg_db_uri
    celery_app.conf.dashboard_username = username
    celery_app.conf.dashboard_password = password
    celery_app.task(name="dashboard_cleaning")(dashboard_cleaning)

    from celery import __version__ as celery_version
    for status, threshold in cleaning_thresholds.items():
        if celery_version.startswith('4'):
            beat_schedule_name = "beat_schedule"
        else:
            beat_schedule_name = "CELERYBEAT_SCHEDULE"
        getattr(celery_app.conf, beat_schedule_name)['clean-%s-tasks' % status.lower()] = {
            'task': 'dashboard_cleaning',
            'schedule': threshold,
            'args': (status, threshold),
            'options': {
                'queue': 'celery_dashboard',
                'expires': 10 * 60
            }
        }
