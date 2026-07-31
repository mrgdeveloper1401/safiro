from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models

from apps.auth_app.enums import VerificationStatus, DocumentType
from apps.core_app.models import ModifyMixin, ActiveMixin, Image


class User(AbstractUser):
    """
    کاربر
    """
    username_validator = UnicodeUsernameValidator()

    phone = models.CharField(_("شماره تلفن"), max_length=15, unique=True)
    is_verify_phone = models.BooleanField(_("شماره تایید شده!"), default=False)
    is_passenger = models.BooleanField(
        _("ایا مسافر هست!"), default=True, db_default=True
    )
    is_driver = models.BooleanField(_("ایا راننده هست!"), default=False)
    is_developer = models.BooleanField(_("توسعه دهنده"), default=False)
    email = models.EmailField(_("ایمیل"), blank=True, null=True)
    first_name = models.CharField(_("نام"), max_length=100, blank=True)
    last_name = models.CharField(_("نام خوانوادگی"), max_length=100, blank=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ("email", "username", "is_developer")

    def clean(self):
        # چک برای هر دو حالت ایجاد و ویرایش
        if self.email:
            # در زمان ویرایش، خود شیء را از کوئری خارج می‌کنیم
            existing = User.objects.filter(email=self.email)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({"email": "ایمیل از قبل وجود دارد"})

        if self.username:
            existing = User.objects.filter(username=self.username)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({"username": "نام کاربری از قبل وجود دارد"})

        return super().clean()

    class Meta:
        db_table = "auth_user"


class Passenger(ModifyMixin):
    """
    مسافر
    """

    # id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False, verbose_name=_("کلید اصلی"))
    user = models.OneToOneField(
        verbose_name=_("کاربر"),
        to=User,
        on_delete=models.PROTECT,
        related_name="user_passengers",
    )
    image = models.ForeignKey(
        verbose_name=_("عکس کاربر"),
        to=Image,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    disable_account = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_passenger"


class CarBrand(ModifyMixin, ActiveMixin):
    brand_name = models.CharField(
        _("برند ماشین"), max_length=100, unique=True
    )  # تویوتا، هیوندای

    class Meta:
        db_table = "car_brand"


class CarModel(ModifyMixin, ActiveMixin):
    brand = models.ForeignKey(
        CarBrand, on_delete=models.PROTECT, verbose_name=_("برند ماشین")
    )
    model_name = models.CharField(max_length=50)  # کمری، سانتافه

    class Meta:
        db_table = "car_model"


class Car(ModifyMixin, ActiveMixin):
    name = models.CharField(_("نام ماشین"), max_length=100)  # "تویوتا کمری 2020"
    brand = models.ForeignKey(
        CarBrand, on_delete=models.PROTECT, verbose_name=_("برند")
    )
    model = models.ForeignKey(CarModel, on_delete=models.PROTECT, verbose_name=_("مدل"))
    year = models.PositiveIntegerField(
        _("سال تولید"), choices=[(y, y) for y in range(1300, 1410)]
    )

    class Meta:
        db_table = "car"


class Driver(ModifyMixin):
    """
    راننده
    """

    # id = models.UUIDField(primary_key=True, default=uuid_7_timestamp, editable=False)
    user = models.OneToOneField(
        verbose_name=_("کاربر"),
        to=User,
        on_delete=models.PROTECT,
        related_name="user_driver",
    )
    image = models.ForeignKey(
        to=Image,
        on_delete=models.PROTECT,
        verbose_name=_("عکس پروفایل"),
        blank=True,
        null=True,
    )
    nation_code = models.CharField(_("کد ملی"), max_length=10, null=True, unique=True)
    father_name = models.CharField(_("نام پدر"), max_length=50, blank=True)
    license_number = models.CharField(
        _("شماره پلاک"), max_length=20, null=True, unique=True
    )
    verification_status = models.CharField(
        _("تایید پروفایل"),
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.CREATED,
    )
    disable_account = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_driver_profile"


class DriverCar(ModifyMixin, ActiveMixin):
    driver = models.ForeignKey(
        to=Driver,
        verbose_name=_("راننده"),
        on_delete=models.PROTECT,
    )
    car = models.ForeignKey(
        to=Car,
        verbose_name=_("ماشین"),
        on_delete=models.PROTECT,
        null=True,
    )

    class Meta:
        db_table = "auth_driver_car"


class DriverDocument(ModifyMixin, ActiveMixin):
    """
    مدارک راننده
    """

    driver = models.ForeignKey(
        verbose_name=_("راننده"),
        on_delete=models.PROTECT,
        related_name="profile_docs",
        to=Driver,
    )
    doc_type = models.CharField(
        _("نوع مدارک"), max_length=15, choices=DocumentType.choices
    )
    image = models.ForeignKey(
        verbose_name=_("عکس"),
        on_delete=models.PROTECT,
        related_name="image_driver_docs",
        to=Image,
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
        related_name="user_notifications",
    )
    title = models.CharField(_("عنوان"), max_length=200)
    body = models.TextField(_("متن"))

    class Meta:
        ordering = ("id",)
        db_table = "auth_user_notification"
