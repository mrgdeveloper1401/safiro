from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .enums import VerificationStatus
from .models import (
    User,
    Passenger,
    Driver,
    UserNotification,
    DriverDocument,
    CarBrand,
    CarModel,
    Car,
    DriverCar,
)
from apps.core_app.models import Image


class DriverDocumentInline(admin.TabularInline):
    model = DriverDocument
    extra = 0
    fields = ("doc_type", "is_verified", "verifier_note")
    readonly_fields = ("doc_type",)
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_editable = ("is_active", "is_verify_phone", "is_passenger", "is_driver")
    filter_horizontal = ()
    ordering = ("-id",)
    list_display_links = ("id", "phone", "email")
    list_display = (
        "id",
        "phone",
        "email",
        "is_verify_phone",
        "is_passenger",
        "is_driver",
        "is_active",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_verify_phone",
        "is_passenger",
        "is_driver",
    )
    search_fields = (
        "phone",
        "username",
    )
    search_help_text = _(
        "برای جست و جو میتوانید از شماره موبایل و نام کاربری استفاده کیند"
    )

    fieldsets = (
        (_("اطلاعات ورود"), {"fields": ("phone", "password")}),
        (_("مشخصات شخصی"), {"fields": ("email", "username")}),
        (
            _("نقش‌ها و وضعیت"),
            {
                "fields": (
                    "is_verify_phone",
                    "is_passenger",
                    "is_driver",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        # (_('دسترسی‌ها'), {
        #     'fields': ('groups', 'user_permissions')
        # }),
        (_("تاریخ‌ها"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone",
                    "password1",
                    "password2",
                    "email",
                    "username",
                    "is_verify_phone",
                    "is_passenger",
                    "is_driver",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    actions = ("disable_user", "enable_user")
    readonly_fields = ("last_login", "date_joined")
    list_per_page = 25

    @admin.action(description="disable user")
    def disable_user(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="enable user")
    def enable_user(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_by_id",
        "get_user_phone",
        "image_type",
        "width",
        "height",
        "size",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("created_by__phone",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل کاربر استفاده کنید")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-id",)
    list_per_page = 25
    raw_id_fields = ("created_by",)
    actions = ("disable_field", "enable_field")
    list_display_links = ("id", "created_by_id", "get_user_phone")

    def get_user_phone(self, obj):
        return obj.created_by.phone

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("created_by")
            .only(
                "created_by_id__phone",
                "image_type",
                "width",
                "height",
                "is_active",
                "created_at",
                "updated_at",
                "size",
            )
        )

    @admin.action(description="disable field")
    def disable_field(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="enable field")
    def enable_field(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "get_user_phone",
        "first_name",
        "last_name",
        "created_at",
    )
    search_fields = ("user__phone",)
    search_help_text = _("برای سرچ میتوانید از شماره تلفن کاربر استفاده کنید")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-id",)
    # autocomplete_fields = ('user', 'image')
    raw_id_fields = ("image", "user")
    list_display_links = ("id", "user_id", "get_user_phone")

    def get_user_phone(self, obj):
        return obj.user.phone

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .only(
                "user__phone",
                "user__first_name",
                "user__last_name",
                "created_at",
                "updated_at",
                "image_id",
            )
        )


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "user_phone",
        "nation_code",
        "license_number",
        "verification_status_colored",
        "created_at",
    )
    list_filter = ("verification_status",)
    search_fields = ("nation_code", "user__phone")
    search_help_text = _(
        "برای جست و جو میتوانید از شماره ملی کاربر یا شماره تماس استفاده کنید"
    )
    inlines = (DriverDocumentInline,)
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("image", "user")
    list_display_links = ("id", "first_name", "last_name", "nation_code", "user_phone")

    def user_phone(self, obj):
        return obj.user.phone

    user_phone.short_description = "شماره تلفن"

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .only(
                "user__first_name",
                "user__last_name",
                "user__phone",
                "image_id",
                "created_at",
                "updated_at",
                "license_number",
                "nation_code",
                "verification_status",
                "father_name",
            )
        )

    def verification_status_colored(self, obj):
        color_map = {
            VerificationStatus.SUBMITTED: "gray",
            VerificationStatus.APPROVED: "green",
            VerificationStatus.REJECTED: "red",
        }
        color = color_map.get(obj.verification_status, "black")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_verification_status_display(),
        )

    verification_status_colored.short_description = "وضعیت تایید"


@admin.register(DriverCar)
class DriverCarAdmin(admin.ModelAdmin):
    raw_id_fields = ("driver", "car")
    list_display = (
        "id",
        "driver_id",
        "car_id",
        "driver_phone",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "driver_id", "car_id")
    list_per_page = 30
    list_editable = ("is_active",)
    search_fields = ("driver__id", "car__id", "driver__user__phone")
    list_filter = ("is_active",)
    list_select_related = ("driver__user",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل راننده استفاده کنید")

    def driver_phone(self, obj):
        return obj.driver.user.phone

    def get_queryset(self, request):
        fields = (
            "is_active",
            "created_at",
            "updated_at",
            "driver__user__phone",
            "car_id",
        )
        return super().get_queryset(request).only(*fields)


@admin.register(DriverDocument)
class DriverDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "driver_id",
        "get_driver_phone",
        "doc_type",
        "is_verified",
        "is_active",
        "verifier_note",
        "created_at",
    )
    list_filter = ("doc_type", "is_verified")
    search_fields = ("profile__user__phone",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل کاربر استفاده کنید")
    ordering = ("-id",)
    list_display_links = ("id", "driver_id", "get_driver_phone")
    raw_id_fields = ("driver", "image")
    list_editable = ("is_verified", "is_active")

    def get_driver_phone(self, obj):
        return obj.driver.user.phone

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("driver__user")
            .only(
                "driver__user__phone",
                "doc_type",
                "is_verified",
                "verifier_note",
                "created_at",
                "updated_at",
                "is_active",
            )
        )


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = (
        "id",
        "user_id",
        "get_user_phone",
        "title",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("user__phone",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل کاربر استفاده کنید")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-id",)
    list_per_page = 25
    actions = ("disable_field", "enable_field")
    list_display_links = ("id", "user_id", "get_user_phone")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .only(
                "user__phone",
                "title",
                "body",
                "is_active",
                "created_at",
                "updated_at",
            )
        )

    def get_user_phone(self, obj):
        return obj.user.phone

    @admin.action(description="disable field")
    def disable_field(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="enable field")
    def enable_field(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ("id", "brand_name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    list_per_page = 30
    search_fields = ("brand_name", "id")
    list_editable = ("is_active",)
    search_help_text = _("برای جست و جو میتوانید از نام برند استفاده کنید")
    list_display_links = ("id", "brand_name")


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "brand_name",
        "model_name",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active",)
    list_per_page = 30
    search_fields = ("brand__brand_name", "id")
    search_help_text = _("برای جست و جو میتوانید از نام برند استفاده کنید")
    raw_id_fields = ("brand",)
    list_display_links = ("id", "brand_name", "model_name")
    list_editable = ("is_active",)
    list_select_related = ("brand",)

    def brand_name(self, obj):
        return obj.brand.brand_name

    def get_queryset(self, request):
        fields = (
            "brand__brand_name",
            "model_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        return super().get_queryset(request).only(*fields)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "brand_name",
        "model_name",
        "year",
        "is_active",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("brand", "model")
    list_display_links = ("id", "name")
    list_editable = ("is_active",)
    list_select_related = ("brand", "model")
    list_filter = ("is_active",)
    search_fields = ("brand__brand_name", "id", "model__model_name")
    search_help_text = _(
        "برای جست و جو میتوانید از نام برند یا نام مدل ماشین استفاده کنید"
    )

    def brand_name(self, obj):
        return obj.brand.brand_name

    def model_name(self, obj):
        return obj.model.model_name

    def get_queryset(self, request):
        fields = (
            "name",
            "brand__brand_name",
            "model__model_name",
            "is_active",
            "created_at",
            "updated_at",
            "year",
        )
        return super().get_queryset(request).only(*fields)
