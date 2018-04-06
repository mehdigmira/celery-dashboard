from functools import wraps
from flask import request, Response, current_app


def check_auth(username, password):
    conf = current_app.celery_app.conf
    return username == conf.dashboard_username and password == conf.dashboard_password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        conf = current_app.celery_app.conf
        if conf.dashboard_username and conf.dashboard_password:
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
        return f(*args, **kwargs)

    return decorated
