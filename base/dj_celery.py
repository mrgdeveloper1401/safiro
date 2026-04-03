from celery import Celery

app = Celery('dj_celery')

app.config_from_object('django.conf', namespace='CELERY')

app.autodiscover_tasks()
