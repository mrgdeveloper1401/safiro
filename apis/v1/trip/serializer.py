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
        passenger = Passenger.objects.filter(user_id=user_id).values("id").first()
        if not passenger:
            raise NotFound("Passenger not found")

        attrs["passenger_id"] = passenger.get("id")
        return attrs
