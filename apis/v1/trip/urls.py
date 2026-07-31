from rest_framework.urls import path
from rest_framework.routers import SimpleRouter

from .views import TripTypeView, ReverseGeocodeView, TripView

app_name = "v1_trip"
router = SimpleRouter()
router.register("trips", TripView, basename="trips")

urlpatterns = [
    path("trip_type", TripTypeView.as_view(), name="trip_type"),
    path("reverse_geocode", ReverseGeocodeView.as_view(), name="reverse_geocode"),
] + router.urls
