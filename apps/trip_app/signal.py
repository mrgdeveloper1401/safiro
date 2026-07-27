from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.trip_app.models import TripType


@receiver(post_save, sender=TripType)
def clear_cache_trip_type(sender, created, **kwargs):
    cache.delete('trip_type')
