from setuptools import setup, find_packages


setup(
  name='celery-dashboard',
  entry_points={
    'celery.commands': [
      'dashboard = celery_dashboard.command:CeleryDashboard',
    ],
  },
  install_requires=["SQLAlchemy==1.1.5", "Flask==0.12", "Flask-SQLAlchemy==2.1", "celery==4.0.2", "celery[redis]",
                    "psycopg2", "python-dateutil==2.6.1 "],
  packages=find_packages()
)
