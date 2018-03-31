import subprocess

import os
import psutil as psutil
import pytest
import signal
import time

from redis import StrictRedis
from sqlalchemy import create_engine


class CeleryWorker(object):
    def __init__(self, with_backend=True):
        self.flush_db()
        self.flush_redis()
        self.started = False
        self.with_backend = with_backend

    def flush_redis(self):
        redis_instance = StrictRedis()
        redis_instance.flushall()

    def flush_db(self):
        from ..celery_dashboard.models import session_ctx_manager
        with session_ctx_manager() as session:
            session.execute("TRUNCATE celery_jobs.tasks")
            session.commit()

    def start(self):
        self.flush_db()
        self.flush_redis()
        self.stop()

        env = os.environ.copy()
        env["C_FORCE_ROOT"] = 'true'

        suffix = ""
        if not self.with_backend:
            suffix = "_no_backend"
        self.worker_process = subprocess.Popen(["celery", "-A", "app.tests.celery_app%s" % suffix,
                                                "worker", "-l", "DEBUG"],
                                               cwd="/", shell=False, env=env)
        self.started = True

    def stop(self):
        if self.started:
            self.kill()
            self.worker_process = None
            self.started = False

    def kill(self):
        os.kill(self.worker_process.pid, signal.SIGTERM)
        for _ in range(2000):
            if self.process_is_killed():
                return
            time.sleep(0.01)
        assert False, "Could not kill celery processes"

    def process_is_killed(self):
        try:
            if psutil.Process(self.worker_process.pid).status() == 'zombie':
                return True
        except psutil.NoSuchProcess:
            return True


@pytest.yield_fixture
@pytest.fixture(scope="function")
def celery_worker():
    celery_worker = CeleryWorker(with_backend=True)
    yield celery_worker
    celery_worker.stop()


@pytest.yield_fixture
@pytest.fixture(scope="function")
def celery_worker_no_backend():
    celery_worker = CeleryWorker(with_backend=False)
    yield celery_worker
    celery_worker.stop()


@pytest.fixture(scope="module", autouse=True)
def ensure_postgresql():
    subprocess.call(["/etc/init.d/postgresql", "start"])
    from .conf import PG_URI
    from ..celery_dashboard.models import SessionMaker, prepare_models
    db_engine = create_engine(PG_URI, client_encoding='utf8', convert_unicode=True, echo='debug', isolation_level="READ COMMITTED")
    SessionMaker.configure(bind=db_engine)
    prepare_models(db_engine)


@pytest.fixture(scope="module", autouse=True)
def ensure_redis():
    subprocess.call(["/etc/init.d/redis-server", "start"])


