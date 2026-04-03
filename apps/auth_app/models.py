from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

from apps.auth_app.enums import VerificationStatus, DocumentType
from apps.core_app.models import ModifyMixin, ActiveMixin, Image


class User(AbstractUser):
    """
    کاربر
    """
    # id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False, verbose_name=_("کلید اصلی"))
    phone = models.CharField(_("شماره تلفن"), max_length=15, unique=True)
    is_verify_phone = models.BooleanField(_("شماره تایید شده!"), default=False)
    is_passenger = models.BooleanField(_("ایا مسافر هست!"), default=True, db_default=True)
    is_driver = models.BooleanField(_("ایا راننده هست!"), default=False)
    email = models.EmailField(_("ایمیل"), blank=True, null=True)
    first_name = models.CharField(_("نام"), max_length=100, blank=True)
    last_name = models.CharField(_("نام خوانوادگی"), max_length=100, blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ('email', "username")

    class Meta:
        db_table = 'auth_user'


class Passenger(ModifyMixin):
    """
    مسافر
    """
    # id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False, verbose_name=_("کلید اصلی"))
    user = models.OneToOneField(
        verbose_name=_("کاربر"),
        to=User,
        on_delete=models.PROTECT,
        related_name="user_passengers"
        )
    image = models.ForeignKey(
        verbose_name=_("عکس کاربر"),
        to=Image,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'auth_passenger'


class Driver(ModifyMixin):
    """
    راننده
    """
    # id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False)
    user = models.OneToOneField(
        verbose_name=_("کاربر"),
        to=User,
        on_delete=models.PROTECT,
        related_name="user_driver"
    )
    image = models.ForeignKey(
        to=Image,
        on_delete=models.PROTECT,
        verbose_name=_("عکس پروفایل"),
        blank=True,
        null=True
    )
    nation_code = models.CharField(_("کد ملی"), max_length=10, null=True, unique=True)
    father_name = models.CharField(_("نام پدر"), max_length=50, blank=True)
    license_number = models.CharField(_("شماره پلاک"), max_length=20, null=True, unique=True)
    verification_status = models.CharField(
        _("تایید پروفایل"),
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SUBMITTED,
    )
    note = models.TextField(_("یادداشت"), blank=True, null=True)
    car_name = models.CharField(_("نام ماشین"), max_length=50, blank=True, null=True) #TODO, remove blank and null when clean migration

    class Meta:
        db_table = 'auth_driver_profile'


class DriverDocument(ModifyMixin, ActiveMixin):
    """
    مدارک راننده
    """
    profile = models.ForeignKey(
        verbose_name=_("راننده"),
        on_delete=models.PROTECT,
        related_name="profile_docs",
        to=Driver,
    )
    doc_type = models.CharField(_("نوع مدارک"), max_length=15, choices=DocumentType.choices)
    image = models.ForeignKey(
        verbose_name=_("عکس"),
        on_delete=models.PROTECT,
        related_name="image_driver_docs",
        to=Image
    )
    is_verified = models.BooleanField(_("تایید شده!"), default=False)
    verifier_note = models.TextField(_("یادداشت"), blank=True, null=True)

    class Meta:
        # unique_together = ("profile", "doc_type")
        db_table = "auth_driver_document"


class UserNotification(ModifyMixin, ActiveMixin):
    """
    نوتیفیکیشن
    """
    user = models.ForeignKey(
        verbose_name=_("کاربر"),
        to=User,
        on_delete=models.PROTECT,
        related_name="user_notifications"
    )
    title = models.CharField(_("عنوان"), max_length=200)
    body = models.TextField(_("متن"))

    class Meta:
        ordering = ("id",)
        db_table = 'auth_user_notification'


# class RequestLog(ModifyMixin, ActiveMixin):
#     phone = models.CharField(
#         _("شماره همراه"),
#         max_length=15,
#         validators=(
#             PhoneNumberValidator(),
#         )
#     )
#     ip_address = models.GenericIPAddressField(_("ای اپی کاربر"))
#     user_agent = models.TextField(_("شناسه مرورگر"), null=True, blank=True)
#     BEHAVIOR_TYPES = (
#         ('multiple_failed_attempts', _("تلاش‌های ناموفق متعدد")),
#         ('rapid_requests', _("درخواست‌های سریع")),
#         ('suspicious_location', _("موقعیت جغرافیایی مشکوک")),
#         ('unusual_activity', _("فعالیت غیرعادی")),
#         ('brute_force', _("حمله brute force")),
#         ('account_takeover', _("تصاحب حساب")),
#         ('credential_stuffing', _("پرکردن اعتبار")),
#     )
#     behavior_type = models.CharField(
#         _("نوع رفتار مشکوک"),
#         max_length=50,
#         choices=BEHAVIOR_TYPES
#     )
#
#     class Meta:
#         db_table = 'auth_request_log'
