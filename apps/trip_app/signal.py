from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.trip_app.models import TripType, Trip
from apps.trip_app.tasks import create_notification_trip_celery


@receiver(post_save, sender=TripType)
def clear_cache_trip_type(sender, created, **kwargs):
    cache.delete('trip_type')

@receiver(post_save, sender=Trip)
def send_notification_after_save_trip(sender, created, instance, **kwargs):
    user_id = instance.passenger.user_id
    status = instance.status

    transaction.on_commit(
        lambda : create_notification_trip_celery.delay(user_id=user_id, status=status)
    )
