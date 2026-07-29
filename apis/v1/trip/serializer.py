from rest_framework.serializers import ModelSerializer, Serializer, FloatField

from apps.trip_app.models import TripType


class TripTypeSerializer(ModelSerializer):
    class Meta:
        model = TripType
        fields = ("id", "trip_name")


class ReverseGeocodeSerializer(Serializer):
    lat = FloatField()
    lng = FloatField()
