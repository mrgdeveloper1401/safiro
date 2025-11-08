import random
import time

from adrf.views import APIView as AsyncAPIView
from django.core.cache import cache
from rest_framework import status

from apis.v1.auth.serializers import RequestOtpSerializer
from apis.v1.utils.custom_permissions import AsyncRemoveAuthenticationPermissions
from apis.v1.utils.custom_response import response
from apis.v1.utils.custome_throttle import OtpRateThrottle
from auth_app.models import User
from base.utils.send_sms import send_sms


class RequestOtpView(AsyncAPIView):
    serializer_class = RequestOtpSerializer
    permission_classes = (AsyncRemoveAuthenticationPermissions,)
    throttle_classes = (OtpRateThrottle,)

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["mobile_phone"]

        user, created = await User.objects.aget_or_create(phone=phone, is_passenger=True, username=phone)

        # generate otp
        otp_code = random.randint(100000, 999999)
        ip = request.META.get("REMOTE_ADDR", "unknown")
        cache_key = f"otp_{phone}_{ip}"

        await cache.aset(cache_key, otp_code, timeout=120)

        # send sms
        await send_sms(phone, otp_code)

        return response(
            success=True,
            result={
                "mobile": phone,
                "exp_time": int(time.time() + 120)
            },
            error=False,
            status_code=status.HTTP_200_OK
        )
