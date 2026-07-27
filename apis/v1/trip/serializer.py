from rest_framework.serializers import ModelSerializer

from apps.trip_app.models import TripType


class TripTypeSerializer(ModelSerializer):
    class Meta:
        model = TripType
        fields = ("id", "trip_name")
