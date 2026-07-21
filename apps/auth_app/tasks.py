import logging

from celery import shared_task
from base.utils.send_sms import send_sms_sorna


@shared_task(bind=True, max_retries=2, queue="send_otp")
def send_otp_sms_celery(self, phone, otp_code):
    try:
        send_sms_sorna(phone, otp_code)
    except Exception as e:
        logging.error("failed to send otp code", exc_info=e)
        raise self.retry(exc=e, countdown=5)
