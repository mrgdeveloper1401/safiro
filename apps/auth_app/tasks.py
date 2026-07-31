# app/auth_app/tasks.py
import logging

from celery import shared_task
from base.utils.send_sms import send_sms_sorna
from apps.auth_app.models import UserNotification


@shared_task(bind=True, max_retries=2, queue="send_otp")
def send_otp_sms_celery(self, phone, otp_code):
    try:
        send_sms_sorna(phone, otp_code)
    except Exception as e:
        logging.error("failed to send otp code", exc_info=e)
        raise self.retry(exc=e, countdown=5)


@shared_task(bind=True, max_retries=2, queue="notifications")
def create_notification_celery(self, title, body, user_id):
    try:
        UserNotification.objects.create(title=title, body=body, user_id=user_id)
    except Exception as e:
        logging.error("failed to create notification", exc_info=e)
        raise self.retry(exc=e, countdown=5)
