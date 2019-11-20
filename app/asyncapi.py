# adapted from: https://stackoverflow.com/a/55440793
# see also: https://stackoverflow.com/questions/31866796/making-an-asynchronous-task-in-flask
# N.B.: for scalability this should be done e.g. with celery

import time
import uuid
import threading
from functools import wraps
from flask import current_app, request, abort, url_for
from flask_login import login_required
from werkzeug.exceptions import HTTPException, InternalServerError
from .main import main

tasks = {}


@main.before_app_first_request
def before_first_request():
    """Start a background thread that cleans up old tasks."""
    def clean_old_tasks():
        """
        This function cleans up old tasks from our in-memory data structure.
        """
        global tasks
        while True:
            # Only keep tasks that are running or that finished less than 5
            # minutes ago.
            five_min_ago = time.time()-5*60
            tasks = {task_id: task for task_id, task in tasks.items()
                     if 'completion_timestamp' not in task or task['completion_timestamp'] > five_min_ago}
            time.sleep(60)

    if not current_app.config['TESTING']:
        thread = threading.Thread(target=clean_old_tasks)
        thread.start()


def async_api(wrapped_function):
    @wraps(wrapped_function)
    def wrapper(*args, **kwargs):
        def task_call(task_id, flask_app, environ):
            # create a request context similar to that of the original request
            # so that the task can have access to flask.g, flask.request, etc.
            with flask_app.request_context(environ):
                try:
                    tasks[task_id]['return_value'] = wrapped_function(*args, **kwargs)
                except HTTPException as e:
                    # TODO:
                    # Sometimes a ClientDisconnected error happens here, which is due to the initial HTTP
                    # request and results in a HTTP 400 response. For lack of a better solution, we should
                    # encourage the client side to send the original request again.
                    tasks[task_id]['return_value'] = current_app.handle_http_exception(e)
                except Exception as e:
                    # the function raised an exception, so we set a 500 error
                    tasks[task_id]['return_value'] = InternalServerError()
                    if current_app.debug:
                        # we want to find out if something happened, so reraise
                        raise
                finally:
                    # we record the time of the response, to help in garbage collecting old tasks
                    tasks[task_id]['completion_timestamp'] = time.time()

        # assign an id to the asynchronous task
        task_id = uuid.uuid4().hex

        # record the task, and then launch it
        tasks[task_id] = {'task_thread': threading.Thread(
            target=task_call, args=(task_id,
                                    current_app._get_current_object(),
                                    request.environ))}
        tasks[task_id]['task_thread'].start()

        # return a 202 response, with a link that the client can use to
        # obtain task status
        return 'accepted', 202, {'Location': url_for('main.get_task_status', task_id=task_id)}
    return wrapper


@main.route('/gettaskstatus', methods=['GET'])
@login_required
def get_task_status():
    """
    Return status about an asynchronous task. If this request returns a 202
    status code, it means that task hasn't finished yet. Else, the response
    from the task is returned.
    """
    task_id = request.args.get('task_id')
    if task_id is None:
        abort(404)
    task = tasks.get(task_id)
    if task is None:
        abort(404)
    if 'return_value' not in task:
        return '', 202, {'Location': url_for('main.get_task_status', task_id=task_id)}
    return task['return_value']
