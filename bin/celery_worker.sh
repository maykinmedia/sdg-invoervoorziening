#!/bin/bash

set -e

toplevel=$(git rev-parse --show-toplevel)
cd "$toplevel/src"

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}
CONCURRENCY=${CELERY_WORKER_CONCURRENCY:-1}

QUEUE=${1:-${CELERY_WORKER_QUEUE:=celery}}
WORKER_NAME=${2:-${CELERY_WORKER_NAME:="${QUEUE}"@%n}}

echo "Starting celery worker $WORKER_NAME with queue $QUEUE"
exec python -m celery -A sdg.conf worker \
    -Q $QUEUE \
    -n $WORKER_NAME \
    -l $LOGLEVEL \
    -O fair \
    -c $CONCURRENCY

