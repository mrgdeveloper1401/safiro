from rest_framework.exceptions import NotFound
from rest_framework.serializers import ModelSerializer, Serializer, FloatField

from apps.auth_app.models import Passenger
from apps.trip_app.models import TripType, Trip


class TripTypeSerializer(ModelSerializer):
    class Meta:
        model = TripType
        fields = ("id", "trip_name")


class ReverseGeocodeSerializer(Serializer):
    lat = FloatField()
    lng = FloatField()


class TripSerializer(ModelSerializer):
    class Meta:
        model = Trip
        exclude = ("is_active",)
        read_only_fields = ("passenger",)

    def validate(self, attrs):
        user_id = self.context["request"].user.id
        passenger_id = Passenger.objects.filter(user_id=user_id).only('user_id')
        if not passenger_id:
            raise NotFound("Passenger not found")

        attrs["passenger_id"] = passenger_id
        return attrs

    def create(self, validated_data):
        passenger_id = self.validated_data.pop("passenger_id")
        return Trip.objects.create(passenger_id=passenger_id, **validated_data)
