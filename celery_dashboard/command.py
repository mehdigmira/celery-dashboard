from celery.bin.base import Command

from .api.app import get_app


class CeleryDashboard(Command):
    def add_arguments(self, parser):
        parser.add_argument(
            '--port', help='Port to use', type=int
        )

    def run(self, port=5000, **kwargs):
        flask_app = get_app(self.app)
        flask_app.run(host="0.0.0.0", port=port)
