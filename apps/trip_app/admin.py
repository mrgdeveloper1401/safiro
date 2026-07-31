from django.contrib import admin

from .models import Trip, TripType, TripReservation, TripPrice


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    raw_id_fields = ("passenger", "trip_type")
    readonly_fields = ("from_lat", "from_lng", "to_lat", "to_lng", "from_address", "to_address")
    list_display = ("id", "passenger_id", 'passenger_phone', "trip_type_name", "status")
    list_select_related = ("passenger__user", "trip_type")
    list_filter = ("status", "is_active", "created_at")
    list_per_page = 30
    list_display_links = ("id", "passenger_id", "passenger_phone")

    def passenger_phone(self, obj):
        return obj.passenger.user.phone

    def trip_type_name(self, obj):
        return obj.trip_type.trip_name

    def get_queryset(self, request):
        fields = (
            "status",
            "passenger__user__phone",
            'trip_type__trip_name',
        )
        return super().get_queryset(request).only(*fields)


@admin.register(TripType)
class TripTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "trip_name", "trip_image_id", "is_active", "created_at")
    list_display_links = ("id", "trip_name")
    list_filter = ("is_active", "created_at")
    list_editable = ("is_active",)
    list_per_page = 20


@admin.register(TripReservation)
class TripReservationAdmin(admin.ModelAdmin):
    raw_id_fields = ("trip", "driver")
    list_display = ("id", "trip_id", "driver_id", "is_active", "created_at")
    list_field = ("is_active", "created_at")
    list_per_page = 30


@admin.register(TripPrice)
class TripPriceAdmin(admin.ModelAdmin):
    list_display = ("id", "distance_km", "price_per_km", "traffic_factor", "is_active", "created_at", "calc_final_price")
    list_per_page = 30
    list_display_links = ("id", "distance_km", "price_per_km")
