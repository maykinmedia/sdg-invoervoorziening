#!/bin/bash

toplevel=$(git rev-parse --show-toplevel)

cd "$toplevel/src"
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

cd $toplevel
src/manage.py makemigrations
