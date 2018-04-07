import os
from flask import Blueprint, send_from_directory

from ..auth import requires_auth

static = Blueprint('static', __name__, url_prefix='/static')


@static.route("/<folder>/<file>")
@requires_auth
def tasks(folder, file):
    folder_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/dist/static", folder)

    return send_from_directory(folder_directory, file)
