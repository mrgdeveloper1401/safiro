from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from .models import User, Passenger, Driver


@receiver(post_save, sender=User)
def create_passenger_or_driver(sender, instance, created, **kwargs):
    if instance.is_passenger:
        passenger, _ = Passenger.objects.get_or_create(user=instance)
    if instance.is_driver:
        driver, _ = Driver.objects.get_or_create(user=instance)

#
# @receiver(post_save, sender=Driver)
# def update_verification_status(sender, instance, **kwargs):
#     if instance.verification_status in ("approved", "rejected"):
#         instance.verification_status = "submitted"
#         instance.save()
