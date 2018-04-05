from contextlib import contextmanager
from logging import getLogger

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

MyResultModelBase = declarative_base()

SessionMaker = sessionmaker()

logger = getLogger(__name__)


@contextmanager
def session_ctx_manager():
    session = SessionMaker()
    try:
        yield session
    except:
        session.rollback()
        session.close()
        raise
    else:
        session.commit()
        session.close()


def prepare_models(engine):
    with engine.begin() as conn:
        pg_version = list(conn.execute("SELECT version();"))[0][0].split(" ")[1]
        pg_version_numbers = list(map(int, pg_version.split(".")))
        if pg_version_numbers[0] < 9 or (pg_version_numbers[0] == 9 and pg_version_numbers[1] < 5):
            logger.error("You should have a PostgreSQL version >= 9.5")
            return
        conn.execute("CREATE SCHEMA IF NOT EXISTS celery_jobs")
    MyResultModelBase.metadata.create_all(engine)

    # this happens pre-fork, so we need to dispose the engine on the main process as well
    engine.dispose()
    return True


class Task(MyResultModelBase):
    """Task result/status."""

    __tablename__ = 'tasks'
    __table_args__ = {'schema': 'celery_jobs'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    task_id = sa.Column(sa.Text, unique=True)
    status = sa.Column(sa.Text, index=True)
    name = sa.Column(sa.Text, default=None, index=True)
    routing_key = sa.Column(sa.String(50), default=None, index=True)
    result = sa.Column(sa.TEXT, nullable=True)
    args = sa.Column(sa.TEXT, nullable=True)
    kwargs = sa.Column(sa.TEXT, nullable=True)
    meta = sa.Column(JSONB, nullable=True)
    date_done = sa.Column(sa.DateTime(timezone=True), nullable=True, index=True)
    date_queued = sa.Column(sa.DateTime(timezone=True), nullable=True, index=True)
    date_started = sa.Column(sa.DateTime(timezone=True), nullable=True, index=True)
    eta = sa.Column(sa.DateTime(timezone=True), nullable=True, index=True)
    exception_type = sa.Column(sa.Text, default=None, index=True, nullable=True)
    traceback = sa.Column(sa.Text, nullable=True)

    def __init__(self, task_id):
        self.task_id = task_id

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status': self.status,
            'result': self.result,
            'traceback': self.traceback,
            'date_done': self.date_done,
            'date_queued': self.date_queued,
            'date_started': self.date_started,
            'eta': self.eta,
            'name': self.name,
            'routing_key': self.routing_key,
            'exception_type': self.exception_type,
            'kwargs': self.kwargs,
            'args': self.args,
            'meta': self.meta
        }

    @property
    def serialized(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status': self.status,
            'result': self.result,
            'traceback': self.traceback,
            'date_queued': self.date_queued.isoformat() if self.date_queued else None,
            'date_done': self.date_done.isoformat() if self.date_done else None,
            'date_started': self.date_started.isoformat() if self.date_started else None,
            'eta': self.eta.isoformat() if self.eta else None,
            'name': self.name,
            'routing_key': self.routing_key,
            'exception_type': self.exception_type,
            'kwargs': self.kwargs,
            'args': self.args,
            'meta': self.meta
        }

    @classmethod
    def upsert(cls, task_id, on_conflict_update=None, **opts):
        if on_conflict_update is None:
            on_conflict_update = opts
        table = cls.__table__
        insert_stmt = insert(table).values(task_id=task_id, **opts)
        stm = insert_stmt.on_conflict_do_update(
            index_elements=[table.c.task_id],
            set_=on_conflict_update
        )
        with session_ctx_manager() as session:
            session.execute(stm)

    def __repr__(self):
        return '<Task {0.task_id} state: {0.status}>'.format(self)
