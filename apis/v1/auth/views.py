import datetime
import random
import time

from adrf.views import APIView as AsyncAPIView
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from rest_framework import status, mixins, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from pytz import timezone as pytz_timezone
from asgiref.sync import sync_to_async

from apis.v1.auth.serializers import (
    RequestOtpSerializer,
    OtpVerifySerializer,
    LoginPhonePasswordSerializer,
    VerifyForgetPassword,
    UserNotificationSerializer,
    DriverSerializer,
    UploadImageSerializer,
    DriverDocSerializer,
    SignUpByPhoneSerializer,
    ResetPasswordSerializer,
    RequestLogVerifyPhoneSerializer
)
from apis.v1.utils.custom_exceptions import UserExistsException, PasswordNotMathException, AccountIsVerified
from apis.v1.utils.custom_permissions import AsyncRemoveAuthenticationPermissions, NotAuthenticated
from apis.v1.utils.custom_response import response
from apis.v1.utils.custome_throttle import OtpRateThrottle
from auth_app.models import User, UserNotification, Driver, DriverDocument, RequestLogVerifyPhone
from base.settings import SIMPLE_JWT
from base.utils.send_sms import send_sms


class SignUpByPhoneView(AsyncAPIView):
    """
    ثبت نام با شماره همراه و پسورد
    """
    serializer_class = SignUpByPhoneSerializer
    permission_classes = (NotAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.data.get('phone')
        password = serializer.data.get('password')
        confirm_password = serializer.data.get('confirm_password')

        # chek user
        check_user =  User.objects.only("is_passenger", "is_verify_phone", "is_active", "phone", "is_staff").filter(phone=phone)
        if check_user.exists():
            raise UserExistsException()
        else:
            # check password
            if password != confirm_password:
                raise PasswordNotMathException()
            # create user
            User.objects.create_user(username=phone, phone=phone, password=password)
            # create token
            get_user =  check_user.first()
            token = RefreshToken.for_user(get_user)
            iran_timezone = pytz_timezone("Asia/Tehran")
            expire_timestamp = int(time.time()) + SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].seconds
            expire_date = datetime.datetime.fromtimestamp(expire_timestamp, tz=iran_timezone)
            data = {
                "mobile": get_user.phone,
                "is_staff": get_user.is_staff,
                "is_verify_phone": get_user.is_verify_phone,
                "is_passenger": get_user.is_passenger,
                "access_token": str(token.access_token),
                "refresh_token": str(token),
                "jwt": "Bearer",
                "expire_timestamp_access_token": expire_timestamp,
                "expire_date_access_token": expire_date
            }
            # return data
            return response(
                success=True,
                status_code=201,
                error=False,
                result=data
            )


class RequestOtpView(AsyncAPIView):
    serializer_class = RequestOtpSerializer
    permission_classes = (AsyncRemoveAuthenticationPermissions,)
    throttle_classes = (OtpRateThrottle,)

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["mobile_phone"]

        await User.objects.aget_or_create(phone=phone, is_passenger=True, username=phone)

        # generate otp
        otp_code = random.randint(100000, 999999)
        ip = request.META.get("REMOTE_ADDR", "X_FORWARDED_FOR")
        cache_key = f"otp_{phone}_{ip}"

        await cache.aset(cache_key, otp_code, timeout=120)

        # send sms
        await send_sms(phone, str(otp_code))

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
                error="کد اشتباه هست یا منقضی شده هست",
                status_code=404
            )
        else:
            user = await User.objects.filter(mobile_phone=phone).only(
                "mobile_phone",
                "is_active",
                "is_staff",
                "is_verify_phone",
                "is_passenger"
            ).afirst()
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
                    "is_staff": user.is_staff,
                    "is_verify_phone": user.is_verify_phone,
                    "is_passenger": user.is_passenger,
                    "access_token": str(token.access_token),
                    "refresh_token": str(token),
                    "jwt": "Bearer",
                    "expire_timestamp_access_token": expire_timestamp,
                    "expire_date_access_token": expire_date
                }
                await cache.adelete(redis_key)
                await User.objects.filter(mobile_phone=phone).aupdate(is_verify_phone=True) # update is_verify_phone user
                return response(
                    success=True,
                    result=data,
                    error=False,
                )


class LoginPhonePasswordView(APIView):
    serializer_class = LoginPhonePasswordSerializer
    permission_classes = (NotAuthenticated, )

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
                "is_passenger": user.is_passenger,
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


class RequestForgetPasswordView(AsyncAPIView):
    serializer_class = RequestOtpSerializer
    permission_classes = (AsyncRemoveAuthenticationPermissions, )

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        # check user dose exists
        user = await sync_to_async(User.objects.only("is_active"))(phone=phone, is_active=True)
        if not await user.aexists():
            return response(
                success=False,
                result={},
                error="کاربر مورد نظر پیدا نشد",
                status_code=404
            )
        else:
            # set key in redis
            otp_code = random.randint(100000, 999999)
            ip = request.META.get("REMOTE_ADDR", "unknown")
            cache_key = f"otp_{phone}_{ip}_{otp_code}"
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


class VerifyForgetPasswordView(AsyncAPIView):
    permission_classes = (AsyncRemoveAuthenticationPermissions, )
    serializer_class = VerifyForgetPassword

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]
        password = serializer.validated_data["password"]
        confirm_password = serializer.validated_data["confirm_password"]

        # check password
        if password != confirm_password:
            return response(
                success=False,
                result={},
                status_code=400,
                error="رمز عبور یکسان نمیباشد"
            )

        # check otp
        get_ip = request.META.get("REMOTE_ADDR", "X-FORWARDED-FOR")
        redis_key = f'otp_{phone}_{get_ip}_{code}'
        check_key = await cache.aget(redis_key)
        if check_key is None:
            return response(
                success=False,
                result={},
                error="کد اشتباه یا انقضا شده هست",
                status_code=404
            )

        else:
            # check user
            user = await sync_to_async(
                User.objects.only("is_active", "is_staff", "is_verify_phone","phone", "is_passenger").filter
            )(phone=phone)
            user_first = await user.afirst()
            if user_first.is_active is False:
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
                    "is_staff": user.is_staff,
                    "is_verify_phone": user.is_verify_phone,
                    "is_passenger": user.is_passenger,
                    "access_token": str(token.access_token),
                    "refresh_token": str(token),
                    "jwt": "Bearer",
                    "expire_timestamp_access_token": expire_timestamp,
                    "expire_date_access_token": expire_date
                }
                await cache.adelete(redis_key) # delete redis key
                # set new password
                hash_password = make_password(password=password)
                await user.aupdate(is_verify_phone=True, password=hash_password) # update user
                return response(
                    success=True,
                    result=data,
                    error=False,
                    status_code=200
                )


class UserNotificationView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = UserNotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserNotification.objects.filter(user_id=self.request.user.id).only(
            "title",
            "body",
            "created_at",
            "updated_at",
        )


class UploadImageView(APIView):
    serializer_class = UploadImageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(success=True, result=serializer.data, error=False, status_code=status.HTTP_201_CREATED)


class DriverView(viewsets.ModelViewSet):
    """
    ثبت نام راننده و مشاهده اطلاعات ثبت نامی
    """
    serializer_class = DriverSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Driver.objects.filter(
            user_id=self.request.user.id
        ).select_related("image").only(
            "first_name",
            "last_name",
            "image",
            "nation_code",
            "father_name",
            "license_number",
            "verification_status",
            "image__image"
        )


class DriverDocView(viewsets.ModelViewSet):
    serializer_class = DriverDocSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return DriverDocument.objects.filter(
            profile__user_id=self.request.user.id,
            is_active=True
        ).select_related("image").only(
            "doc_type",
            "is_verified",
            "verifier_note",
            "image__image"
        )


class ResetPasswordView(APIView):
    """
    رسیت پسورد
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        result = {
            "message": "پسورد شما با موفقیت تغییر یافت"
        }
        return response(
            success=True,
            result=result,
            error=False
        )


class RequestLogVerifyPhoneView(AsyncAPIView):
    """
    درخواست تایید شماره همراه
    """
    serializer_class = RequestLogVerifyPhoneSerializer

    async def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        ip = request.META.get("REMOTE_ADDR", "X_FORWARDED_FOR")

        # save log
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        await RequestLogVerifyPhone.objects.acreate(phone=phone, ip_address=ip, user_agent=user_agent)

        # check
        user = await User.objects.filter(
            phone=phone,
            is_active=True
        ).only("is_verify_phone").afirst()
        # check user dose exists
        if not user:
            raise NotFound("حساب کاربری با این شماره وجود ندارد")
        else:
            # check user is verified?
            if user.is_verify_phone:
                raise AccountIsVerified()
            else:
                # generate otp
                otp_code = random.randint(100000, 999999)
                cache_key = f"otp_{phone}_{ip}"

                # set in redis
                await cache.aset(cache_key, otp_code, timeout=120)

                # send sms
                await send_sms(phone, str(otp_code))

                return response(
                    success=True,
                    result={
                        "mobile": phone,
                        "exp_time": int(time.time() + 120),
                        "message": "کد تایید برای شما ارسال شد"
                    },
                    error=False,
                    status_code=status.HTTP_200_OK
                )
