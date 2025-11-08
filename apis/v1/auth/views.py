import datetime
import random
import time

from adrf.views import APIView as AsyncAPIView
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from pytz import timezone as pytz_timezone

from apis.v1.auth.serializers import RequestOtpSerializer, OtpVerifySerializer, LoginPhonePasswordSerializer
from apis.v1.utils.custom_permissions import AsyncRemoveAuthenticationPermissions, SyncRemoveAuthenticationPermissions
from apis.v1.utils.custom_response import response
from apis.v1.utils.custome_throttle import OtpRateThrottle
from auth_app.models import User
from base.settings import SIMPLE_JWT
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


class OtpVerifyView(AsyncAPIView):
    serializer_class = OtpVerifySerializer
    permission_classes = (AsyncRemoveAuthenticationPermissions,)

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['mobile_phone']
        otp = serializer.validated_data['otp']

        # get in redis
        get_ip = request.META.get('REMOTE_ADDR', "X-FORWARDED-FOR")
        redis_key = f'{phone}_{get_ip}_{otp}'
        get_redis_key = await cache.aget(redis_key)
        if get_redis_key is None:
            return response(
                success=False,
                result={},
                error="پردازش موفق نبود",
                status_code=404
            )
        else:
            user = await User.objects.filter(mobile_phone=phone).only("mobile_phone", "is_active").afirst()
            if user.is_active is False:
                return response(
                    success=False,
                    result={},
                    error="حساب کاربری شما مسدود هست",
                    status_code=404
                )
            else:
                token = RefreshToken.for_user(user)
                iran_timezone = pytz_timezone("Asia/Tehran")
                expire_timestamp = int(time.time()) + SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].seconds
                expire_date = datetime.datetime.fromtimestamp(expire_timestamp, tz=iran_timezone)
                data = {
                    "mobile": phone,
                    "access_token": str(token.access_token),
                    "refresh_token": str(token),
                    "jwt": "Bearer",
                    "expire_timestamp_access_token": expire_timestamp,
                    "expire_date_access_token": expire_date
                }
                await cache.adelete(redis_key)
                return response(
                    success=True,
                    result=data,
                    error=False,
                )


class LoginPhonePasswordView(APIView):
    serializer_class = LoginPhonePasswordSerializer
    permission_classes = (SyncRemoveAuthenticationPermissions, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get data
        phone = serializer.validated_data["phone"]
        password = serializer.validated_data["password"]

        # check user
        user = authenticate(request, phone=phone, password=password)
        if user is None:
            return response(
                success=False,
                result={},
                error="نام کاربری یا رمز عبور اشتباه هست",
                status_code=404
            )
        else:
            token = RefreshToken.for_user(user)
            iran_timezone = pytz_timezone("Asia/Tehran")
            expire_timestamp = int(time.time()) + SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].seconds
            expire_date = datetime.datetime.fromtimestamp(expire_timestamp, tz=iran_timezone)
            data = {
                "mobile": phone,
                "is_verify_phone": user.is_verify_phone,
                "is_staff": user.is_staff,
                "access_token": str(token.access_token),
                "refresh_token": str(token),
                "jwt": "Bearer",
                "expire_timestamp_access_token": expire_timestamp,
                "expire_date_access_token": expire_date
            }
            return response(
                success=True,
                result=data,
                error=False,
            )
