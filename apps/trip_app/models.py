from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.auth_app.models import Driver, Passenger
from apps.core_app.models import ActiveMixin, ModifyMixin

STATUS_CHOICES = [
    ('pending', 'در انتظار'),
    ('confirmed', 'تایید شده'),
    ('in_progress', 'در حال انجام'),
    ('completed', 'تکمیل شده'),
    ('cancelled', 'لغو شده'),
    ("reserve", "رزور سفر")
]

class Trip(ActiveMixin, ModifyMixin):
    driver = models.ForeignKey(
        Driver,
        verbose_name=_("راننده"),
        on_delete=models.PROTECT,
    )
    passenger = models.ForeignKey(
        Passenger,
        verbose_name=_("مسافر"),
        on_delete=models.PROTECT,
        related_name="passenger_trips",
    )
    from_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    from_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    to_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    to_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    number_of_passenger = models.PositiveIntegerField(_("تعداد مسافران"), default=4)
    price_per_seat = models.DecimalField(_("قیمت کل"), max_digits=10, decimal_places=0)
    status = models.CharField(_("وضعیت سفر"), max_length=20, choices=STATUS_CHOICES, default='pending')
    departure_time = models.DateTimeField(_("زمان سفر"), null=True, blank=True)
    reserve_for_other = models.BooleanField(_("رزور برای دیگر"), default=False)
    phone_reserve_for_other = models.CharField(_("شماره تماس رزور کننده دیگر"), blank=True, null=True)

    class Meta:
        db_table = "trip"
