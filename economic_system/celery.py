import os
from celery import Celery
from django.conf import settings

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'economic_system.settings.base')
app = Celery()
app.conf.update(settings.CELERY)
