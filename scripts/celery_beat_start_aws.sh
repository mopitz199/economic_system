#!/bin/bash

python manage.py migrate postgres_extensions
python manage.py migrate
sleep 1m
celery -A economic_system beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler