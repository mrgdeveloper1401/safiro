from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.auth_app.models import Driver, Passenger
from apps.core_app.models import ActiveMixin, ModifyMixin

STATUS_CHOICES = [
    ("pending", "در انتظار"),
    ("confirmed", "تایید شده"),
    ("completed", "تکمیل شده"),
    ("cancelled", "لغو شده"),
    ("reserve", "رزور سفر"),
]


class Trip(ActiveMixin, ModifyMixin):
    # TODO, when clean migration, remove null and blank
    passenger = models.ForeignKey(
        Passenger,
        verbose_name=_("مسافر"),
        on_delete=models.PROTECT,
        related_name="passenger_trips",
    )
    trip_type = models.ForeignKey("TripType", on_delete=models.PROTECT, null=True)

    from_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    from_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    from_address = models.CharField(max_length=255, null=True)

    to_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    to_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    to_address = models.CharField(max_length=255, null=True)

    status = models.CharField(
        _("وضعیت سفر"), max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    departure_time = models.DateTimeField(_("زمان سفر"), null=True, blank=True)
    reserve_for_other = models.BooleanField(_("رزور برای دیگر"), default=False)
    phone_reserve_for_other = models.CharField(
        _("شماره تماس رزور کننده دیگر"), blank=True, null=True
    )

    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "trip"


class TripReservation(ActiveMixin, ModifyMixin):
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name="trip_reservations")
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name="driver_reservations")

    class Meta:
        db_table = "reservation"


class TripType(ModifyMixin, ActiveMixin):
    trip_name = models.CharField(max_length=255)
    trip_image = models.ForeignKey(
        "core_app.Image",
        on_delete=models.PROTECT,
        related_name="trip_image",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "trip_type"


class TripPrice(ActiveMixin, ModifyMixin):
    distance_km = models.DecimalField(
        _("فاصله (کیلومتر)"),
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    price_per_km = models.DecimalField(
        _("قیمت هر کیلومتر"),
        max_digits=6,
        decimal_places=2,
        default=0.00,
    )
    traffic_factor = models.PositiveSmallIntegerField(
        _("فاکتور ترافیک"),
        default=1.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    @property
    def calc_final_price(self):
        price = self.distance_km * self.price_per_km
        traffic_price = price * self.traffic_factor / 100
        price += traffic_price
        return price

    class Meta:
        db_table = "trip_price"
        verbose_name = _("قیمت سفر")
        verbose_name_plural = _("قیمت‌های سفر")
