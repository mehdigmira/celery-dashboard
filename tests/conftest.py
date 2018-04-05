import subprocess

import os
import psutil as psutil
import pytest
import signal
import time

from redis import StrictRedis
from sqlalchemy import create_engine


class ProcessFixture(object):
    def __init__(self, *args, **kwargs):
        self.started = False

    def stop(self):
        if self.started:
            self.kill()
            self.process = None
            self.started = False

    def kill(self):
        os.kill(self.process.pid, signal.SIGTERM)
        for _ in range(2000):
            if self.process_is_killed():
                return
            time.sleep(0.01)
        assert False, "Could not kill celery processes"

    def process_is_killed(self):
        try:
            if psutil.Process(self.process.pid).status() == 'zombie':
                return True
        except psutil.NoSuchProcess:
            return True

    def start_process(self, cmd, env=None):
        popen_kwargs = {"cwd": "/", "shell": False}
        if env:
            popen_kwargs["env"] = env
        self.process = subprocess.Popen(cmd, **popen_kwargs)
        self.started = True


class Api(ProcessFixture):
    def __init__(self, app_name="celery_app"):
        ProcessFixture.__init__(self)
        self.api_url = "http://localhost:5000/api/"
        self.app_name = app_name

    def start(self):
        self.stop()

        env = os.environ.copy()
        env["C_FORCE_ROOT"] = 'true'

        cmd = ["celery", "-A", "app.tests.%s" % self.app_name, "dashboard"]
        self.start_process(cmd, env=env)


class CeleryWorker(ProcessFixture):
    def __init__(self, app_name="celery_app"):
        ProcessFixture.__init__(self)
        self.flush_db()
        self.flush_redis()
        self.app_name = app_name

    def flush_redis(self):
        redis_instance = StrictRedis()

        all_keys = redis_instance.keys("*")

        # with celery 3 if we use flushall, we'll have errors concerning missing kombu bindings
        for key in all_keys:
            if "_kombu" not in str(key):
                redis_instance.delete(key)

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
        self.start_process(cmd, env=env)


@pytest.yield_fixture
@pytest.fixture(scope="function")
def celery_worker():
    celery_worker = CeleryWorker()
    yield celery_worker
    celery_worker.stop()


@pytest.yield_fixture
@pytest.fixture(scope="function")
def api():
    api = Api()
    yield api
    api.stop()


@pytest.yield_fixture
@pytest.fixture(scope="function")
def celery_worker_no_backend():
    celery_worker = CeleryWorker(app_name="celery_app_no_backend")
    yield celery_worker
    celery_worker.stop()


@pytest.yield_fixture
@pytest.fixture(scope="function")
def api_no_backend():
    api = Api(app_name="celery_app_no_backend")
    yield api
    api.stop()


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


@pytest.fixture(scope="module", autouse=True)
def install():
    subprocess.call(["pip", "install", "-e", "."], cwd="/app")


