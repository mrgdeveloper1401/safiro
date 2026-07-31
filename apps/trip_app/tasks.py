from celery import shared_task

from apps.auth_app.models import UserNotification


@shared_task(queue="notifications", bind=True, max_retries=2)
def create_notification_trip_celery(self, user_id, status):
    try:
        if status == "pending":
            UserNotification.objects.create(
                user_id=user_id, title="ثبت سفر", body="درخواست سفر شما ثبت شد"
            )
        if status == "reserve":
            UserNotification.objects.create(
                user_id=user_id, title="رزور سفر", body="درخواست رزور سفر شما ثبت شد"
            )
        if status == "confirmed":
            UserNotification.objects.create(
                user_id=user_id,
                title="تایید سفر",
                body="درخواست  سفر شما ثبت شد توسط راننده ای تایید شد",
            )
        if status == "completed":
            UserNotification.objects.create(
                user_id=user_id, title="تکمیل سفر", body="سفر شما پایان و تکمیل شد"
            )
        if status == "cancelled":
            UserNotification.objects.create(
                user_id=user_id, title="لغو سفر", body="سفر شما لغو شد"
            )
    except Exception as e:
        raise self.retry(exc=e)
