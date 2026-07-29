from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.cache import cache

from apps.trip_app.models import TripType
from base.utils.neshan import reverse_geocode
from .serializer import TripTypeSerializer, ReverseGeocodeSerializer
from ...utils.custom_response import response


class TripTypeView(APIView):
    serializer_class = TripTypeSerializer

    def get(self, request):
        queryset = TripType.objects.filter(is_active=True).only("trip_name")
        serializer = self.serializer_class(queryset, many=True)

        # check in cache
        res = cache.get('trip_type')
        if res:
            return response(success=True, result=res, error=False, status_code=200)
        else:
            cache.set('trip_type', serializer.data)
            return response(success=True, result=serializer.data, error=False, status_code=200)


class ReverseGeocodeView(APIView):
    serializer_class = ReverseGeocodeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # request into api
        lat, lng = serializer.validated_data['lat'], serializer.validated_data['lng']
        result = reverse_geocode(lat, lng)

        return response(success=True, result=result, error=False, status_code=200)
