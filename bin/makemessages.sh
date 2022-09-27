#!/bin/bash
cd src/

echo "Extracting messages for Python code..."

python manage.py makemessages --all
python manage.py compilemessages
