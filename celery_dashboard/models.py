from datetime import datetime

from celery import current_app
from celery import states
from celery.backends.database import session_cleanup
from celery.backends.database.session import _after_fork_cleanup_session
from celery.five import python_2_unicode_compatible
import sqlalchemy as sa
from sqlalchemy import PickleType
from kombu.utils.compat import register_after_fork
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

MyResultModelBase = declarative_base()


class SessionManager(object):
  """Manage SQLAlchemy sessions."""

  def __init__(self):
    self._engines = {}
    self._sessions = {}
    self.forked = False
    self.prepared = False
    if register_after_fork is not None:
      register_after_fork(self, _after_fork_cleanup_session)

  def _after_fork(self):
    self.forked = True

  def get_engine(self, dburi, **kwargs):
    if self.forked:
      try:
        return self._engines[dburi]
      except KeyError:
        engine = self._engines[dburi] = create_engine(dburi, **kwargs)
        return engine
    else:
      return create_engine(dburi, poolclass=NullPool)

  def create_session(self, dburi, short_lived_sessions=False, **kwargs):
    engine = self.get_engine(dburi, **kwargs)
    if self.forked:
      if short_lived_sessions or dburi not in self._sessions:
        self._sessions[dburi] = sessionmaker(bind=engine)
      return engine, self._sessions[dburi]
    else:
      return engine, sessionmaker(bind=engine)

  def prepare_models(self, engine):
    with engine.begin() as conn:
      conn.execute("CREATE SCHEMA IF NOT EXISTS celery_jobs")
    if not self.prepared:
      MyResultModelBase.metadata.create_all(engine)
      self.prepared = True

  def session_factory(self, dburi, **kwargs):
    engine, session = self.create_session(dburi, **kwargs)
    self.prepare_models(engine)
    return session()


@python_2_unicode_compatible
class Task(MyResultModelBase):
  """Task result/status."""

  __tablename__ = 'tasks'
  __table_args__ = {'schema': 'celery_jobs'}

  task_id = sa.Column(sa.Text, unique=True, primary_key=True, autoincrement=False)
  status = sa.Column(sa.Text, index=True)
  name = sa.Column(sa.Text, default=None, index=True)
  routing_key = sa.Column(sa.String(50), default=None, index=True)
  result = sa.Column(JSONB, nullable=True)
  args = sa.Column(JSONB, nullable=True)
  kwargs = sa.Column(JSONB, nullable=True)
  date_done = sa.Column(sa.DateTime, nullable=True, index=True)
  date_queued = sa.Column(sa.DateTime, nullable=True, index=True)
  eta = sa.Column(sa.DateTime, nullable=True, index=True)
  exception_type = sa.Column(sa.Text, default=None, index=True, nullable=True)
  traceback = sa.Column(sa.Text, nullable=True)

  def __init__(self, task_id):
    self.task_id = task_id

  def to_dict(self):
    return {
      'task_id': self.task_id,
      'status': self.status,
      'result': self.result,
      'traceback': self.traceback,
      'date_done': self.date_done,
      'date_queued': self.date_queued,
      'eta': self.eta,
      'name': self.name,
      'routing_key': self.routing_key,
      'exception_type': self.exception_type,
      'kwargs': self.kwargs,
      'args': self.args
    }

  @property
  def serialized(self):
    return {
      'task_id': self.task_id,
      'status': self.status,
      'result': self.result,
      'traceback': self.traceback,
      'date_queued': self.date_queued.isoformat() if self.date_queued else None,
      'date_done': self.date_done.isoformat() if self.date_done else None,
      'eta': self.eta.isoformat() if self.eta else None,
      'name': self.name,
      'routing_key': self.routing_key,
      'exception_type': self.exception_type,
      'kwargs': self.kwargs,
      'args': self.args,
    }

  @classmethod
  def upsert(cls, task_id, on_conflict_do_nothing=False, **opts):
    table = cls.__table__
    insert_stmt = insert(table).values(task_id=task_id, **opts)
    if on_conflict_do_nothing:
      stm = insert_stmt.on_conflict_do_nothing(constraint=table.primary_key)
    else:
      stm = insert_stmt.on_conflict_do_update(
        constraint=table.primary_key,
        set_=opts
      )
    session = SessionManager().session_factory(dburi=current_app.conf.dashboard_pg_uri)
    with session_cleanup(session):
      session.execute(stm)
      session.commit()

  def __repr__(self):
    return '<Task {0.task_id} state: {0.status}>'.format(self)
