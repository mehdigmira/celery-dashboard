from flask import Blueprint, send_from_directory

static = Blueprint('static', __name__, url_prefix='/static')


@static.route("/<folder>/<file>")
def tasks(folder, file):
    return send_from_directory("frontend/dist/static/%s" % folder, file)
