#!/bin/bash

set -e

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

mkdir -p celerybeat

while python src/manage.py showmigrations | grep '\[ \]'  &> /dev/null; do
    echo "Waiting for all migrations to be completed, please wait ..."
    sleep 3
done

echo "Starting celery beat"
exec python -m celery -A sdg beat \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler \
    --workdir src \
    -l $LOGLEVEL \
    -s ../celerybeat/beat
