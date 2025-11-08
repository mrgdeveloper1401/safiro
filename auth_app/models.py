from django.contrib.auth.models import AbstractUser
from django.db import models


class ModifyMixin(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    is_verify_phone = models.BooleanField(default=False)
    is_passenger = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)

    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('phone', "first_name", "last_name")

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


class Passenger(ModifyMixin):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='passenger')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'auth_passenger'


class Driver(ModifyMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='drivers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    nation_code = models.CharField(max_length=10)
    license_number = models.CharField(max_length=20)

    class Meta:
        db_table = 'auth_driver'


class UserNotification(ModifyMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'auth_user_notification'


