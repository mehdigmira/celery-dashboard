from setuptools import setup, find_packages


def get_requirements():
    reqs = []
    for filename in ["requirements.txt"]:
        with open(filename, "r") as f:
            reqs += [x.strip() for x in f.readlines()]
    return reqs


setup(
    name='celery-dashboard',
    version='0.0.6',
    entry_points={
        'celery.commands': [
            'dashboard = celery_dashboard.command:CeleryDashboard',
        ],
    },
    install_requires=get_requirements(),
    packages=["celery_dashboard", "celery_dashboard.api"],
    include_package_data=True,
    description="A simple, extensible and full-featured dashboard for celery",
    author="Mehdi GMIRA",
    license='MIT',
    keywords=["celery", "python", "dashboard", "postgresql", "sql", "database"],
    platforms='any'
)
