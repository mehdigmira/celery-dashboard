# Celery Dashboard

![Build Status](https://travis-ci.org/mehdigmira/celery-dashboard.svg?branch=master)

This package allows you to have access to a dashboard for your celery application.
It was built with two main goals:
- Have a persistent and complete view of how your tasks and queues are behaving.
- Have a simple codebase in order for it to be easily extensible.

# Advantages over Flower

- A simple codebase: We use celery's signals api to register all tasks state from being queued to being ran or revoked.
- No single point of failure: Flower spawns a thread that listens to all events. Using the signals api allows us to delegate the work: each worker is responsible of keeping track of its tasks.
- A modern UI (Vue.js + Vuetify)
- Data is stored in a PostgreSQL database, making it persistent and available from anywhere even if your dashboard's webserver happens to crash.
- Allow keeping track of the progress of long running tasks

# Screenshots

![Image of Dashboard](https://image.ibb.co/iPWTMc/jobs_tab.png)
![Image of Dashboard](https://image.ibb.co/hifNgc/run_task.png)
![Image of Dashboard](https://image.ibb.co/dpiuSH/workers_tab.png)


# Requirements & compatibility

A PostgreSQL database >= 9.5 is required.
The code has been tested for celery's versions 3 and 4 running under python 2.7 or 3.

# Getting started

The first thing to do after installing the package is to update the python file where your celery application is created as follows:

```python
from celery import Celery

from celery_dashboard import init

celery_app = Celery('test_app', broker='redis://localhost', backend='redis://localhost')

init(celery_app, "YOU POSTGRES DATABASE URI (e.g postgresql://docker:docker@localhost:5432/docker)", "YOUR DASHBOARD USERNAME", "YOUR DASHBOARD PASSWORD")

@celery_app.task(name="divide")
def div(x, y):
    return x / y

```

That's it ! your app is all setup.
Now if you want to checkout the dashboard you just need to run `celery -A <your_app> dashboard`
And the dashboard will be running on localhost:5000. If you want to specify an other port you can add `--port=<your_port>` to the command line
