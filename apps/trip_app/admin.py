from django.contrib import admin

from .models import Trip, TripType


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    raw_id_fields = ("driver", "passenger")


@admin.register(TripType)
class TripTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "trip_name", "trip_image_id", "is_active", "created_at")
    list_display_links = ("id", "trip_name")
    list_filter = ("is_active", "created_at")
    list_editable = ("is_active",)
    list_per_page = 20
