from celery.bin.base import Command

from . import init
from .api.app import get_app


class CeleryDashboard(Command):

  def add_arguments(self, parser):
    parser.add_argument(
      '--port', help='Port to use'
    )

  def run(self, port=5555, **kwargs):
    flask_app = get_app(self.app)
    flask_app.run(host="0.0.0.0", port=port)
