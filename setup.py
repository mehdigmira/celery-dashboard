from setuptools import setup, find_packages


def get_requirements():
    reqs = []
    for filename in ["requirements.txt"]:
        with open(filename, "r") as f:
            reqs += [x.strip() for x in f.readlines()]
    return reqs


setup(
  name='celery-dashboard',
  version='0.0.1',
  entry_points={
    'celery.commands': [
      'dashboard = celery_dashboard.command:CeleryDashboard',
    ],
  },
  install_requires=get_requirements(),
  packages=find_packages()
)
