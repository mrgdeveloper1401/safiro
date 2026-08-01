from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet

from apps.trip_app.models import TripType, Trip
from base.utils.neshan import reverse_geocode
from .serializer import TripTypeSerializer, ReverseGeocodeSerializer, TripSerializer
from ...utils.custom_response import response
from ...utils.paginations import CustomPagination


class TripTypeView(APIView):
    serializer_class = TripTypeSerializer

    def get(self, request):
        queryset = TripType.objects.filter(is_active=True).only("trip_name")
        serializer = self.serializer_class(queryset, many=True)

        # check in cache
        res = cache.get("trip_type")
        if res:
            return response(success=True, result=res, error=False, status_code=200)
        else:
            cache.set("trip_type", serializer.data)
            return response(
                success=True, result=serializer.data, error=False, status_code=200
            )


class ReverseGeocodeView(APIView):
    serializer_class = ReverseGeocodeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # request into api
        lat, lng = serializer.validated_data["lat"], serializer.validated_data["lng"]
        result = reverse_geocode(lat, lng)

        return response(success=True, result=result, error=False, status_code=200)


class TripView(ModelViewSet):
    """
    status -->     ("pending", "در انتظار"),
    ("confirmed", "تایید شده"),
    ("completed", "تکمیل شده"),
    ("cancelled", "لغو شده"),
    ("reserve", "رزور سفر"), \n

    trip_type --> رزور سفر
    """

    serializer_class = TripSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.request.user.id
        return Trip.objects.filter(is_active=True, passenger__user_id=user_id).order_by(
            "-id"
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['pk'] = self.kwargs.get('pk')
        return context