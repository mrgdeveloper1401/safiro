from celery import Celery
import os

from apps.shop_app.tasks import task_track_event

app = Celery('dj_celery')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
