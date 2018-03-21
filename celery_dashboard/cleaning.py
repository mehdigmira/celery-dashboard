from datetime import datetime, timedelta

from celery import current_app
from celery.backends.database import session_cleanup
from sqlalchemy import and_

from celery_dashboard.models import SessionManager, Task

def dashboard_cleaning(status, threshold):
    tasks_table = Task.__table__
    stm = (tasks_table
           .delete()
           .where(and_(tasks_table.c.status == status,
                       tasks_table.c.date_done <= datetime.utcnow() - timedelta(seconds=threshold))))
    session = SessionManager().session_factory(dburi=current_app.conf.dashboard_pg_uri)
    with session_cleanup(session):
        session.execute(stm)
        session.commit()