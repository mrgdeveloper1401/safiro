from celery import Celery
import os
from apps.auth_app.tasks import send_otp_sms_celery

app = Celery()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
