import subprocess

import os
import psutil as psutil
import pytest
import signal
import time

from redis import StrictRedis
from sqlalchemy import create_engine


class CeleryWorker(object):
    def __init__(self, app_name="celery_app"):
        self.flush_db()
        self.flush_redis()
        self.started = False
        self.app_name = app_name

    def flush_redis(self):
        redis_instance = StrictRedis()
        redis_instance.flushall()

    def flush_db(self):
        from ..celery_dashboard.models import session_ctx_manager
        with session_ctx_manager() as session:
            session.execute("TRUNCATE celery_jobs.tasks")
            session.commit()

    def start(self, beat=False, queue="celery"):
        self.flush_db()
        self.flush_redis()
        self.stop()

        env = os.environ.copy()
        env["C_FORCE_ROOT"] = 'true'

        cmd = ["celery", "-A", "app.tests.%s" % self.app_name, "worker", "-l", "DEBUG", "-Q", queue]
        if beat:
            cmd.append("-B")
        self.worker_process = subprocess.Popen(cmd, cwd="/", shell=False, env=env)
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
    celery_worker = CeleryWorker()
    yield celery_worker
    celery_worker.stop()


@pytest.yield_fixture
@pytest.fixture(scope="function")
def celery_worker_no_backend():
    celery_worker = CeleryWorker(app_name="celery_app_no_backend")
    yield celery_worker
    celery_worker.stop()


@pytest.yield_fixture
@pytest.fixture(scope="function")
def celery_worker_fast_cleaning():
    celery_worker = CeleryWorker(app_name="celery_app_fast_cleaning")
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


