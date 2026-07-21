from hashlib import sha1

from django.db import models
from django.utils.translation import gettext_lazy as _


class ModifyMixin(models.Model):
    created_at = models.DateTimeField(_("تاریخ ایجاد فیلد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ اخرین بروزرسانی فیلد"), auto_now=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    is_active = models.BooleanField(_("قابل نمایش"), default=True)

    class Meta:
        abstract = True


class Image(ModifyMixin, ActiveMixin):
    """
    عکس
    """

    image = models.ImageField(_("عکس"), upload_to="images/%Y/%m/%d")
    created_by = models.ForeignKey(
        verbose_name=_("توسط چه کسی ایجاد شده"),
        to="auth_app.User",
        on_delete=models.PROTECT,
        related_name="user_images",
    )
    width = models.IntegerField(_("عرض"), blank=True, null=True)
    height = models.IntegerField(_("ارتفاع"), blank=True, null=True)
    size = models.IntegerField(_("حجم عکس"), blank=True, null=True)
    image_type = models.CharField(_("فورمت عکس"), max_length=10, blank=True, null=True)

    class Meta:
        db_table = "image"

    @property
    def hash_image(self):
        hasher = sha1()
        for i in self.image.chunks():
            hasher.update(i)
        return hasher.hexdigest()

    def save(self, *args, **kwargs):
        if self.pk:
            old = Image.objects.filter(pk=self.pk).only('image').first()
            if old and old.image == self.image:
                return super().save(*args, **kwargs)

        self.image_size = self.image.size
        self.image_width = self.image.width
        self.image_height = self.image.height
        # self.image_hash = self.hash_image
        return super().save(*args, **kwargs)

    @property
    def get_image_url(self):
        return self.image.url if self.image else None


class MainSettings(ModifyMixin, ActiveMixin):
    is_main_settings = models.BooleanField(default=True)
    header_logo = models.ForeignKey(
        Image, on_delete=models.PROTECT, related_name="header_logo"
    )
    header_phone = models.CharField()
    header_email = models.EmailField()

    class Meta:
        db_table = "main_settings"
