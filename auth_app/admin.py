from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .enums import VerificationStatus
from .models import User, Image, Passenger, Driver, UserNotification, DriverDocument


class DriverDocumentInline(admin.TabularInline):
    model = DriverDocument
    extra = 0
    fields = ("doc_type", "is_verified", "verifier_note")
    readonly_fields = ("doc_type",)
    can_delete = False

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-id',)
    list_display_links = ("id", "phone", 'email')
    list_display = (
        'id', 'phone', 'email', 'first_name', 'last_name',
        'is_verify_phone', 'is_passenger', 'is_driver', 'is_active'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser',
        'is_verify_phone', 'is_passenger', 'is_driver'
    )
    search_fields = ('phone', 'username',)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل و نام کاربری استفاده کیند")

    fieldsets = (
        (_('اطلاعات ورود'), {
            'fields': ('phone', 'password')
        }),
        (_('مشخصات شخصی'), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_('نقش‌ها و وضعیت'), {
            'fields': (
                'is_verify_phone', 'is_passenger', 'is_driver',
                'is_active', 'is_staff', 'is_superuser'
            )
        }),
        (_('دسترسی‌ها'), {
            'fields': ('groups', 'user_permissions')
        }),
        (_('تاریخ‌ها'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone', 'password1', 'password2',
                'first_name', 'last_name', 'email',
                'is_verify_phone', 'is_passenger', 'is_driver',
                'is_active', 'is_staff', 'is_superuser'
            ),
        }),
    )
    actions = ("disable_user", "enable_user")
    readonly_fields = ('last_login', 'date_joined')
    list_per_page = 25

    @admin.action(description="disable user")
    def disable_user(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="enable user")
    def enable_user(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'image_type', 'width', 'height', 'size', 'is_active', 'created_at')
    list_filter = ('is_active', 'image_type')
    search_fields = ('created_by__phone',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-id',)
    list_per_page = 25
    raw_id_fields = ('created_by',)
    actions = ("disable_field", "enable_field")

    @admin.action(description="disable field")
    def disable_field(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="enable field")
    def enable_field(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__phone', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-id',)
    autocomplete_fields = ('user', 'image')


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
        "is_active",
        "created_at",
    )
    list_filter = ("verification_status", "is_active")
    search_fields = ("nation_code",)
    search_help_text = _("برای جست و جو میتوانید از شماره ملی کاربر استفاده کنید")
    inlines = (DriverDocumentInline,)
    ordering = ("-id",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user", "image")
    list_display_links = ("id", "first_name", "last_name", "nation_code")

    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = "شماره تلفن"

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


@admin.register(DriverDocument)
class DriverDocumentAdmin(admin.ModelAdmin):
    raw_id_fields = ("profile",)
    list_display = ("id", "profile", "doc_type", "is_verified", "verifier_note", "created_at")
    list_filter = ("doc_type", "is_verified")
    search_fields = ("profile__user__phone", "profile__first_name", "profile__last_name")
    ordering = ("-id",)


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ('id', 'user', 'title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__phone', 'title', 'body')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-id',)
    list_per_page = 25
    actions = ("disable_field", "enable_field")

    @admin.action(description="disable field")
    def disable_field(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="enable field")
    def enable_field(self, request, queryset):
        queryset.update(is_active=True)
