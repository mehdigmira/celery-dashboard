# celery-dashboard (WIP)

![Build Status](https://api.travis-ci.org/pricingassistant/celery_dashboard.svg?branch=master)

A dashboard to monitor celery tasks. 

Advantages over Celery Flower:
- Easier to understand and extend: Uses the celery signals api to save tasks states.
- A modern UI (Vue.js + Vuetify).
- Data is stored in a postgres database, making it permanent and available from anywhere even if the dashboard's server is not running.
- If you only care about monitoring failed tasks and have strict performance constraints, you can use the `only_store` param.

