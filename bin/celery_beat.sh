#!/bin/bash

set -e

toplevel=$(git rev-parse --show-toplevel)
cd "$toplevel/src"

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

mkdir -p celerybeat

echo "Starting celery beat"
exec python -m celery -A sdg.conf beat \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler \
    -l $LOGLEVEL \
    -s ../celerybeat/beat
