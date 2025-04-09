from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_exchange.settings')

app = Celery('freelance_exchange')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Asia/Tomsk'
app.autodiscover_tasks()
