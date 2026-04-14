#!/bin/bash

src/manage.py dumpdata --indent=4 --natural-foreign --natural-primary --exclude=django_celery_beat.PeriodicTask django_celery_beat > src/sdg/fixtures/django_celery_beat.json
src/manage.py dump_tasks
