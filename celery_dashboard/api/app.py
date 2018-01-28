#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

from celery_dashboard.api.api import api


def get_app(celery_app):
  app = Flask(__name__)

  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config["SQLALCHEMY_DATABASE_URI"] = celery_app.conf.dashboard_pg_uri

  app.db = SQLAlchemy(app)
  app.celery_app = celery_app

  app.register_blueprint(api)

  @app.route("/")
  def index():
    return render_template("index.html")

  return app
