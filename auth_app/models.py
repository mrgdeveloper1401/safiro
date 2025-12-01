from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.db import models

from auth_app.enums import VerificationStatus, DocumentType
from auth_app.validators import PhoneNumberValidator
from base.utils.uuid import uuid_7_timestamp


class ModifyMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    is_active = models.BooleanField(_("حذف"), default=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    """
    کاربر
    """
    id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False, verbose_name=_("کلید اصلی"))
    phone = models.CharField(_("شماره تلفن"), max_length=15, unique=True)
    is_verify_phone = models.BooleanField(_("شماره تایید شده!"), default=False)
    is_passenger = models.BooleanField(_("ایا مسافر هست!"), default=False)
    is_driver = models.BooleanField(_("ایا راننده هست!"), default=False)
    email = models.EmailField(_("ایمیل"), blank=True, null=True)
    first_name = None
    last_name = None

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ('email', "username")

    class Meta:
        db_table = 'auth_user'


class Image(ModifyMixin, ActiveMixin):
    """
    عکس
    """
    image = models.ImageField(_("عکس"), upload_to='images/%Y/%m/%d')
    created_by = models.ForeignKey(
        verbose_name=_("توسط چه کسی ایجاد شده"),
        to=User,
        on_delete=models.PROTECT,
        related_name="user_images"
    )
    width = models.IntegerField(_("عرض"), blank=True, null=True)
    height = models.IntegerField(_("ارتفاع"), blank=True, null=True)
    size = models.IntegerField(_("حجم عکس"), blank=True, null=True)
    image_type = models.CharField(_("فورمت عکس"), max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'auth_image'

    def save(self, *args, **kwargs):
        self.image_type = self.image.url.split(".")[-1]
        self.width = self.image.width
        self.height = self.image.height
        self.size = self.image.size
        super().save(*args, **kwargs)

    @property
    def get_image_url(self):
        return self.image.url if self.image else None


class Passenger(ModifyMixin, ActiveMixin):
    """
    مسافر
    """
    id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False, verbose_name=_("کلید اصلی"))
    user = models.OneToOneField(
        verbose_name=_("کاربر"),
        to=User,
        on_delete=models.PROTECT,
        related_name="user_passengers"
        )
    first_name = models.CharField(_("نام"), max_length=100, blank=True)
    last_name = models.CharField(_("نام خوانوادگی"), max_length=100, blank=True)
    image = models.ForeignKey(
        verbose_name=_("عکس کاربر"),
        to=Image,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'auth_passenger'


class Driver(ModifyMixin, ActiveMixin):
    """
    راننده
    """
    id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False)
    first_name = models.CharField(_("نام"), max_length=100)
    last_name = models.CharField(_("خوانوادگی"), max_length=100)
    user = models.OneToOneField(
        verbose_name=_("کاربر"),
        to=User,
        on_delete=models.PROTECT,
        related_name="user_driver"
    )
    image = models.ForeignKey(
        Image,
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

    class Meta:
        db_table = 'auth_driver_profile'


class DriverDocument(ModifyMixin, ActiveMixin):
    """
    مدارک راننده
    """
    id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False)
    profile = models.ForeignKey(
        verbose_name=_("راننده"),
        on_delete=models.PROTECT,
        related_name="profile_docs",
        to=Driver,
    )
    doc_type = models.CharField(_("نوع مدارک"), max_length=50, choices=DocumentType.choices)
    image = models.ForeignKey(
        verbose_name=_("عکس"),
        on_delete=models.PROTECT,
        related_name="image_driver_docs",
        to="Image",
        null=True, # TODO, when clean migration remove these field
    )
    is_verified = models.BooleanField(_("تایید شده!"), default=False)
    verifier_note = models.TextField(_("یادداشت"), blank=True, null=True)

    class Meta:
        unique_together = ("profile", "doc_type")
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


class RequestLog(ModifyMixin, ActiveMixin):
    phone = models.CharField(
        _("شماره همراه"),
        max_length=15,
        validators=(
            PhoneNumberValidator(),
        )
    )
    ip_address = models.GenericIPAddressField(_("ای اپی کاربر"))
    user_agent = models.TextField(_("شناسه مرورگر"), null=True, blank=True)
    BEHAVIOR_TYPES = (
        ('multiple_failed_attempts', _("تلاش‌های ناموفق متعدد")),
        ('rapid_requests', _("درخواست‌های سریع")),
        ('suspicious_location', _("موقعیت جغرافیایی مشکوک")),
        ('unusual_activity', _("فعالیت غیرعادی")),
        ('brute_force', _("حمله brute force")),
        ('account_takeover', _("تصاحب حساب")),
        ('credential_stuffing', _("پرکردن اعتبار")),
    )
    behavior_type = models.CharField(
        _("نوع رفتار مشکوک"),
        max_length=50,
        choices=BEHAVIOR_TYPES
    )

    class Meta:
        db_table = 'auth_request_log'
