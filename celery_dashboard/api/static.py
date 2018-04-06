from flask import Blueprint, send_from_directory

from ..auth import requires_auth

static = Blueprint('static', __name__, url_prefix='/static')


@static.route("/<folder>/<file>")
@requires_auth
def tasks(folder, file):
    return send_from_directory("frontend/dist/static/%s" % folder, file)
