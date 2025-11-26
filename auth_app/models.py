import imghdr
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

from auth_app.enums import DriverType, Province, VerificationStatus, DocumentType


class ModifyMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
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


class Image(ModifyMixin):
    image = models.ImageField(_("عکس"), upload_to='images/%Y/%m/%d')
    created_by = models.ForeignKey(_("توسط چه کسی ایجاد شده"), User, on_delete=models.PROTECT, related_name="user_images")
    width = models.IntegerField(_("عرض"), blank=True, null=True)
    height = models.IntegerField(_("ارتفاع"), blank=True, null=True)
    size = models.IntegerField(_("حجم عکس"), blank=True, null=True)
    image_type = models.CharField(_("فورمت عکس"), max_length=10, blank=True, null=True)
    is_active = models.BooleanField(_("نمایش برای کاربر"), default=True)

    class Meta:
        db_table = 'auth_image'

    def save(self, *args, **kwargs):
        self.image_type = imghdr.what(self.image)
        self.width = self.image.width
        self.height = self.image.height
        self.size = self.image.size
        super().save(*args, **kwargs)


class Passenger(ModifyMixin):
    """
    مسافر
    """
    user = models.OneToOneField(_("کاربر"), User, on_delete=models.PROTECT, related_name='passenger')
    first_name = models.CharField(_("نام"), max_length=100)
    last_name = models.CharField(_("نام خوانوادگی"), max_length=100)
    image = models.ForeignKey(_("عکس کاربر"), Image, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(_("نمایش برای کاربر"), default=True)

    class Meta:
        db_table = 'auth_passenger'


class Driver(ModifyMixin):
    """
    راننده
    """
    first_name = models.CharField(_("نام"), max_length=100)
    last_name = models.CharField(_("خوانوادگی"), max_length=100)
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='drivers',
        verbose_name=_("کاربر")
    )
    image = models.ForeignKey(Image, on_delete=models.PROTECT, verbose_name=_("عکس پروفایل"))
    is_active = models.BooleanField(_("قابل نمایش برای کاربر"), default=True)
    nation_code = models.CharField(_("کد ملی"), max_length=10)
    father_name = models.CharField(_("نام پدر"), max_length=50)
    license_number = models.CharField(_("شماره پلاک"), max_length=20)
    verification_status = models.CharField(
        _("تایید پروفایل"),
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SUBMITTED,
    )

    class Meta:
        db_table = 'auth_driver_profile'


class DriverDocument(ModifyMixin):
    profile = models.ForeignKey(_("راننده"), Driver, on_delete=models.PROTECT, related_name="documents")
    doc_type = models.CharField(_("نوع مدارک"), max_length=50, choices=DocumentType.choices)
    is_verified = models.BooleanField(_("تایید شده!"), default=False)
    verifier_note = models.TextField(_("یادداشت"), blank=True, null=True)
    is_active = models.BooleanField(_("قابل نمایش برای راننده"), default=True)

    class Meta:
        unique_together = ("profile", "doc_type")
        db_table = "auth_driver_document"


class UserNotification(ModifyMixin):
    user = models.ForeignKey(_("کاربر"), User, on_delete=models.PROTECT, related_name="user_notifications")
    title = models.CharField(_("عنوان"), max_length=200)
    body = models.TextField(_("متن"))
    is_active = models.BooleanField(_("قابل نمایش برای کاربر"), default=True)

    class Meta:
        db_table = 'auth_user_notification'
