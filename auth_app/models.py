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
    phone = models.CharField(max_length=15, unique=True)
    is_verify_phone = models.BooleanField(default=False)
    is_passenger = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ('email', "first_name", "last_name", "username")

    class Meta:
        db_table = 'auth_user'


class Image(ModifyMixin):
    image = models.ImageField(upload_to='images/%Y/%m/%d')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    image_type = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'auth_image'

    def save(self, *args, **kwargs):
        # import ipdb
        # ipdb.set_trace()
        self.image_type = imghdr.what(self.image)
        self.width = self.image.width
        self.height = self.image.height
        self.size = self.image.size
        super().save(*args, **kwargs)

class Passenger(ModifyMixin):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='passenger')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'auth_passenger'


class Driver(ModifyMixin):
    first_name = models.CharField(_("نام"), max_length=100)
    last_name = models.CharField(_("خوانوادگی"), max_length=100)
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='drivers',
        verbose_name=_("کاربر")
    )
    image = models.ForeignKey(Image, on_delete=models.PROTECT, verbose_name=_("عکس پروفایل"))
    is_active = models.BooleanField(default=True)
    nation_code = models.CharField(_("کد ملی"), max_length=10)
    father_name = models.CharField(_("نام پدر"), max_length=50)
    license_number = models.CharField(_("شماره پلاک"), max_length=20)
    verification_status = models.CharField(
        _("تایید پروفایل"),
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.SUBMITTED,
    )
    # driver_type = models.CharField(
    #     _("نوع وسیله"),
    #     max_length=20,
    #     choices=DriverType.choices,
    #     default=DriverType.riding
    # )
    # activity_location = models.CharField(
    #     _("محل فعالیت"),
    #     max_length=50,
    #     choices=Province.choices,
    #     default=Province.FARS
    # )
    # certification_image_one = models.ForeignKey(
    #     Image,
    #     on_delete=models.PROTECT,
    #     related_name="certificate_on",
    #     verbose_name=_("عکس روی گواهی نامه")
    # )
    # certification_image_two = models.ForeignKey(
    #     Image,
    #     on_delete=models.PROTECT,
    #     related_name="certificate_back",
    #     verbose_name=_("عکس پشت گواهی نامه")
    # )
    # car_image_one = models.ForeignKey(
    #     Image,
    #     on_delete=models.PROTECT,
    #     related_name="car_image_on",
    #     verbose_name=_("عکس روی کارت خودرو")
    # )
    # car_image_two = models.ForeignKey(
    #     Image,
    #     on_delete=models.PROTECT,
    #     related_name="car_back",
    #     verbose_name=_("عکس پشت کارت خودرو")
    # )
    # photo_insurance_policy = models.ForeignKey(
    #     Image,
    #     on_delete=models.PROTECT,
    #     related_name="insurance_policy",
    #     verbose_name=_("عکس بیمه نامه")
    # )
    # code_insurance_policy = models.CharField(_("کد یکتای بیمه نامه"), max_length=50)
    # nation_code_insurance_policy = models.CharField(_("کد ملی بیمه نامه"), max_length=15)
    # identity_verification = models.ForeignKey(
    #     Image,
    #     on_delete=models.PROTECT,
    #     verbose_name=_("عکس تایید هویت"),
    #     related_name="identity_verification",
    # )

    class Meta:
        db_table = 'auth_driver_profile'


class DriverDocument(ModifyMixin):
    profile = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name="documents")
    doc_type = models.CharField(_("نوع مدارک"), max_length=50, choices=DocumentType.choices)
    is_verified = models.BooleanField(default=False)
    verifier_note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("profile", "doc_type")
        db_table = "auth_driver_document"


class UserNotification(ModifyMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'auth_user_notification'


