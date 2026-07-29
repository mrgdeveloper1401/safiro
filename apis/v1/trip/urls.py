from rest_framework.urls import path

from .views import TripTypeView, ReverseGeocodeView

app_name = "v1_trip"

urlpatterns = [
    path('trip_type', TripTypeView.as_view(), name="trip_type"),
    path("reverse_geocode", ReverseGeocodeView.as_view(), name="reverse_geocode"),
]
