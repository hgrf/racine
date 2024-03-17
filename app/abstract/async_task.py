import ctypes
import os
import threading
from threading import current_thread
from time import sleep, time
from flask import Flask

_use_celery = not os.getenv("USE_THREADED_ASYNC", False)
if _use_celery:
    from celery import Celery
    from celery import current_task as celery_current_task
    from celery import shared_task as celery_shared_task
    from celery import Task as CeleryTask


def celery_init_app(app: Flask) -> None:
    class FlaskTask(CeleryTask):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.conf.update(
        dict(
            CELERYBEAT_SCHEDULE=dict(
                usage_stats_task=dict(
                    task="usage_stats_task",
                    schedule=60.0,
                )
            )
        )
    )
    celery_app.set_default()
    app.extensions["celery"] = celery_app


class Worker(threading.Thread):
    RESULT_PERSIST_TIME = 5

    def __init__(self, func, name, time_limit, *args, **kwargs):
        super().__init__(target=self._wrapper, args=args, kwargs=kwargs)

        self.func = func
        self.task_name = name

        # register the worker
        global _next_worker_id
        with _workers_lock:
            self.id = str(_next_worker_id)
            self.name = self.id
            _next_worker_id += 1
            _workers[self.id] = self
            print(f"Registered worker for {self.task_name} with ID {self.id}")

        # set up state management
        self.state = "PENDING"
        self.info = {}

        # set up limits for execution time and result persistence
        self.deadline_work = None if time_limit is None else time() + time_limit
        self.deadline_result = None

        # start the worker
        self.start()

    def update_state(self, state, meta):
        self.state = state
        self.info = meta

    def abort(self):
        self.deadline_work = None
        self.deadline_result = time() + Worker.RESULT_PERSIST_TIME
        thread_id = None
        for id, thread in threading._active.items():
            if thread is self:
                thread_id = id
                break
        if thread_id is None:
            print("Thread not found")
            return
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(thread_id), ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)
            print("Exception raise failure")

    def _wrapper(self, *args, **kwargs):
        with _app.app_context():
            self.func(*args, **kwargs)

        self.deadline_work = None
        self.deadline_result = time() + Worker.RESULT_PERSIST_TIME


_app = None
_workers: dict[str, Worker] = {}
_workers_lock = threading.Lock()
_next_worker_id = 1


class Task:
    """
    This is a simple async task implementation that can be used as a drop-in replacement for Celery.
    It is not meant to be used on a server with high load, but it is useful for development, testing
    and for the standalone version of the app.
    """

    def __init__(self, func, name, time_limit):
        self.func = func
        self.name = name
        self.time_limit = time_limit

    def delay(self, *args, **kwargs):
        # run the task in a separate thread
        return Worker(self.func, self.name, self.time_limit, *args, **kwargs)

    def AsyncResult(self, worker_id: str):
        return _workers.get(worker_id)


def monitor_tasks():
    # TODO: implement task scheduling
    while True:
        with _workers_lock:
            workers_to_remove = []
            for id, worker in _workers.items():
                if worker.deadline_work is not None and time() > worker.deadline_work:
                    worker.update_state("FAILURE", {"status": "Time limit exceeded"})
                    worker.abort()
                if worker.deadline_result is not None and time() > worker.deadline_result:
                    workers_to_remove.append(id)
            for id in workers_to_remove:
                print(f"Removing worker {id}")
                del _workers[id]
        sleep(1)


class TaskProxy:
    @staticmethod
    def update_state(state, meta):
        _workers[current_thread().name].update_state(state, meta)


def task_decorator(name, soft_time_limit=None):
    def wrapper(f):
        return Task(f, name, soft_time_limit)

    return wrapper


def async_init_app(app: Flask) -> None:
    global _app
    global _use_celery
    if _use_celery:
        celery_init_app(app)
    else:
        _app = app
        monitor = threading.Thread(target=monitor_tasks)
        monitor.daemon = True
        monitor.start()


current_task = celery_current_task if _use_celery else TaskProxy()
shared_task = celery_shared_task if _use_celery else task_decorator
