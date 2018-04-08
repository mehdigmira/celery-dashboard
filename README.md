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
![Image of Dashboard](https://image.ibb.co/gG3pux/queues_tab.png)
![Image of Dashboard](https://image.ibb.co/mbh4SH/traceback.png)

# Requirements & compatibility

A PostgreSQL database >= 9.5 is required.
The code has been tested for celery version 3 and 4 running under python 2.7 or 3.

# Getting started

The first thing to do after installing the package is to update the python file where your celery application is created as follows:

```python
from celery import Celery

from celery_dashboard import init

celery_app = Celery('test_app', broker='redis://localhost', backend='redis://localhost')

init(celery_app,
     "YOU POSTGRES DATABASE URI (e.g postgresql://docker:docker@localhost:5432/docker)",
     "YOUR DASHBOARD USERNAME", "YOUR DASHBOARD PASSWORD")

@celery_app.task(name="divide")
def div(x, y):
    return x / y

```

That's it ! your app is all setup.
Now if you want to checkout the dashboard you just need to run `celery -A <your_app> dashboard`
And the dashboard will be running on localhost:5000. If you want to specify an other port you can add `--port=<your_port>` to the command line

# Database cleaning

In order to keep you database size under control, the `init()` function will automatically setup some cleaning tasks in your beat schedule.

By default these tasks will clean:
- your SUCCESS tasks that are 4 hours old
- your STARTED tasks that are 1 hour old. In case a worker crashes (killed with a SIGKILL for example) it will not be able to update its running task's status. So this task will stay in a STARTED status forever. In order to clean these tasks, we assume that if a task is in STARTED status for more that an hour, it should be cleaned.

You can of course override this settings by passing the `cleaning_thresholds` paramater to the `init` function. `cleaning_thresholds` is a dict with statuses as keys and thresholds as values (in seconds), such as:
```
{"STARTED": 3600, "SUCCESS": 3600 * 4}
```

All these tasks will be routed to the queue `celery_dashboard`.

So you should have a beat schedule running (`celery -A <your_app> beat`) and a worker that processes tasks in the `celery_dashboard` queue (`celery -A <your_app> worker -Q celery_dashboard`)

