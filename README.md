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
