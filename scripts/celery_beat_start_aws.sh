#!/bin/bash

sleep 2m
celery -A economic_system beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler