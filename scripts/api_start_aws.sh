#!/bin/bash

python manage.py migrate
gunicorn -w 4 economic_system.wsgi -b 0.0.0.0:9000 --timeout 1500 --graceful-timeout 1500 --access-logfile /var/log/gunicorn-access.log --error-logfile /var/log/gunicorn-error.log