from datetime import datetime, timedelta

from sqlalchemy import and_

from .models import session_ctx_manager, Task


def dashboard_cleaning(status, threshold):
    tasks_table = Task.__table__
    stm = (tasks_table
           .delete()
           .where(and_(tasks_table.c.status == status,
                       tasks_table.c.date_done <= datetime.utcnow() - timedelta(seconds=threshold))))
    with session_ctx_manager() as session:
        session.execute(stm)
        session.commit()
