#!/bin/bash

python manage.py migrate postgres_extensions
python manage.py migrate
celery -A economic_system worker