import subprocess

import os
import psutil as psutil
import pytest
import signal
import time

from redis import StrictRedis

from .conf import PG_URI
from ..celery_dashboard.models import session_cleanup, SessionManager


class CeleryWorker(object):
    def __init__(self):
        self.flush_db()
        self.flush_redis()
        self.started = False

    def flush_redis(self):
        redis_instance = StrictRedis()
        redis_instance.flushall()

    def flush_db(self):
        session = SessionManager().session_factory(dburi=PG_URI)
        with session_cleanup(session):
            session.execute("TRUNCATE celery_jobs.tasks")
            session.commit()

    def start(self):
        self.flush_db()
        self.flush_redis()
        self.stop()

        env = os.environ.copy()
        env["C_FORCE_ROOT"] = 'true'
        self.worker_process = subprocess.Popen(["celery", "-A", "app.tests.celery_app", "worker", "-l", "DEBUG"],
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
    celery_worker = CeleryWorker()
    yield celery_worker
    celery_worker.stop()


@pytest.fixture(scope="module", autouse=True)
def ensure_postgresql():
    subprocess.call(["/etc/init.d/postgresql", "start"])


@pytest.fixture(scope="module", autouse=True)
def ensure_redis():
    subprocess.call(["/etc/init.d/redis-server", "start"])
