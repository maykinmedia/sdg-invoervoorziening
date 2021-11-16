#!/bin/bash

src/manage.py dumpdata --indent=4 --natural-foreign --natural-primary django_celery_beat > src/sdg/fixtures/django_celery_beat.json
