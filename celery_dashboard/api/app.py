#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from ..api.static import static
from ..api.api import api


def get_app(celery_app):
    app = Flask(__name__, template_folder="frontend/dist")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = celery_app.conf.dashboard_pg_uri

    app.db = SQLAlchemy(app)
    app.celery_app = celery_app

    app.register_blueprint(api)
    app.register_blueprint(static)

    @app.route("/")
    def index():
        return send_from_directory("frontend/dist", "index.html")

    return app
