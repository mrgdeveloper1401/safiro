import datetime
import random
import time

from adrf.views import APIView as AsyncAPIView
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
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
    VerifyRequestVerifiedPhoneSerializer,
    UserStatusSerializer,
    PassengerSerializer,
    UpdateUserSerializer,
    DriverCarSerializer,
    CarBrandSerializer, CarModelSerializer,
)
from apis.utils.custom_exceptions import (
    UserExistsException,
    PasswordNotMathException,
    AccountIsVerified,
    NotActiveAccount
)
from apis.utils.custom_permissions import AsyncRemoveAuthenticationPermissions, NotAuthenticated, IsDriverAccount
from apis.utils.custom_response import response
from apis.utils.custome_throttle import OtpRateThrottle
from apis.utils.get_ip import get_client_ip
from apis.utils.paginations import CustomPagination
from apps.auth_app.models import User, UserNotification, Driver, DriverDocument, Passenger, DriverCar, CarBrand, \
    CarModel
from base.settings import SIMPLE_JWT
from base.utils.generate import generate_otp, generate_token
from apps.auth_app.tasks import send_otp_sms_celery


class SignUpByPhoneView(APIView):
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
        check_user =  User.objects.only("id").filter(phone=phone)
        if check_user.exists():
            raise UserExistsException()
        else:
            # check password
            if password != confirm_password:
                raise PasswordNotMathException()
            # create user
            create_user = User.objects.create_user(username=phone, phone=phone, password=password)
            # create token
            tk = generate_token(create_user)
            data = {
                "mobile": create_user.phone,
                "is_staff": create_user.is_staff,
                "is_verify_phone": create_user.is_verify_phone,
                "is_passenger": create_user.is_passenger,
                "is_driver": create_user.is_driver,
                "token": tk,
            }
            # return data
            return response(
                success=True,
                status_code=201,
                error=False,
                result=data
            )


class RequestOtpView(APIView):
    """
    درخواست کد otp  \n
    otp_type --> otp, forget_password
    """
    serializer_class = RequestOtpSerializer
    permission_classes = (NotAuthenticated,)
    throttle_classes = (OtpRateThrottle,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        fields = ("is_active", "is_driver", "is_passenger", "is_verify_phone", "phone")
        user = User.objects.filter(phone=phone).only(*fields).first()
        if not user:
            user = User.objects.create_user(username=phone, phone=phone)
        elif not user.is_active:
            raise NotActiveAccount()

        # generate otp
        otp_code = generate_otp()
        ip = get_client_ip(request)
        otp_type = serializer.data.get('otp_type')
        cache_key = f"{otp_type}_{phone}_{ip}_{otp_code}"

        cache.set(cache_key, otp_code, timeout=120)

        # send sms
        send_otp_sms_celery.delay(phone, str(otp_code))

        return response(
            success=True,
            result={
                "mobile": phone,
                "is_passenger": user.is_passenger,
                "is_driver": user.is_driver,
                "is_verify_phone": user.is_verify_phone,
                "is_active": user.is_active,
                "exp_otp_datetime": timezone.now() + datetime.timedelta(minutes=2),
                'exp_otp_time': time.time() + 120,
            },
            error=False,
            status_code=status.HTTP_200_OK
        )


class OtpVerifyView(APIView):
    """
    اعتبار سنجی کد برای ورود به حساب کاربری
    """
    serializer_class = OtpVerifySerializer
    permission_classes = (NotAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['mobile_phone']
        otp = serializer.validated_data['otp']

        # get in redis
        get_ip = get_client_ip(request)
        redis_key = f'otp_{phone}_{get_ip}_{otp}'
        get_redis_key = cache.get(redis_key)
        if get_redis_key is None:
            return response(
                success=False,
                result={},
                error="کد اشتباه هست یا منقضی شده هست",
                status_code=404
            )
        else:
            user = User.objects.filter(phone=phone).only(
                "phone",
                "is_active",
                "is_verify_phone",
                "is_passenger",
                "is_driver"
            ).first()
            if not user.is_active:
                raise NotActiveAccount()
            else:
                user.is_verify_phone = True
                user.save()

                tk = generate_token(user)

                data = {
                    "id": user.pk,
                    "mobile": phone,
                    "is_verify_phone": user.is_verify_phone,
                    "is_passenger": user.is_passenger,
                    "is_driver": user.is_driver,
                    "token": tk,
                }
                cache.delete(redis_key)
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
            tk = generate_token(user)
            data = {
                "mobile": phone,
                "is_verify_phone": user.is_verify_phone,
                "is_staff": user.is_staff,
                "is_passenger": user.is_passenger,
                "token": tk,
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

        phone = serializer.validated_data["mobile_phone"]

        # check user dose exists
        user = await sync_to_async(lambda: User.objects.only("is_active").filter(phone=phone, is_active=True))()
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
            ip = get_client_ip(request)
            cache_key = f"reset_password_{phone}_{ip}_{otp_code}"
            await cache.aset(cache_key, otp_code, timeout=120)

            # send sms
            # await send_sms(phone, str(otp_code))
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
        get_ip = get_client_ip(request)
        redis_key = f'reset_password_{phone}_{get_ip}_{code}'
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
                token = RefreshToken.for_user(user_first)
                iran_timezone = pytz_timezone("Asia/Tehran")
                expire_timestamp = int(time.time()) + SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].seconds
                expire_date = datetime.datetime.fromtimestamp(expire_timestamp, tz=iran_timezone)
                data = {
                    "mobile": phone,
                    "is_staff": user_first.is_staff,
                    "is_verify_phone": user_first.is_verify_phone,
                    "is_passenger": user_first.is_passenger,
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
    """
    pagination --> max_item in page --> 1000 \n
    default item in page --> 20
    """
    serializer_class = UserNotificationSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return UserNotification.objects.filter(
            user_id=self.request.user.id
        ).only(
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


class DriverView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """
    ثبت نام راننده و مشاهده اطلاعات ثبت نامی
    """
    serializer_class = DriverSerializer
    permission_classes = (IsDriverAccount,)

    def get_queryset(self):
        return Driver.objects.filter(
            user_id=self.request.user.id,
        ).select_related(
            "image",
            "user"
        ).only(
            "verification_status",
            "disable_account",
            "image",
            "nation_code",
            "father_name",
            "license_number",
            "image__image",
            "user__username",
            "user__email",
            "user__first_name",
            "user__last_name",
            "user__phone",
            "user__is_verify_phone"
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            result = {
                "message": "شما حساب راننده رو ندارید اگه تمایل به فعال سازی میتوانید ان را درخواست بدید"
            }
            return response(
                success=False,
                error=True,
                result=result,
                status_code=400
            )
        serializer = self.get_serializer(queryset, many=True)
        return response(success=True, error=False, result=serializer.data)


class DriverCarViewSet(viewsets.ModelViewSet):
    serializer_class = DriverCarSerializer
    permission_classes = (IsDriverAccount, )

    def get_queryset(self):
        driver_id = self.kwargs.get("driver_pk")
        user_id = self.request.user.id
        return DriverCar.objects.filter(
            driver_id=driver_id,
            driver__user_id=user_id,
            is_active=True
        ).defer("is_active")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['driver_pk'] = self.kwargs.get("driver_pk")
        return context

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class DriverDocView(viewsets.ModelViewSet):
    """
    مدارک ارسالی \n
    'id_front', _('جلوی کارت شناسایی')
    'id_back', _('پشت کارت شناسایی')
    'car_front', _('جلوی خودرو')
    'car_back', _('پشت خودرو')
    'insurance', _('بیمه')
    'identity_verif', _('تایید هویت')
    "fuel_card", _("کارت سوخت")
    """
    serializer_class = DriverDocSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return DriverDocument.objects.filter(
            driver__user_id=self.request.user.id,
            driver_id=self.kwargs.get("driver_pk"),
            is_active=True
        ).select_related("image").only(
            "doc_type",
            "is_verified",
            "verifier_note",
            "image__image"
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


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


class UserTypeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserStatusSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id).only("is_driver", "is_passenger", "phone", "email", "username")


class PassengerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PassengerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        fields = (
            "user__username",
            "user__first_name",
            "user__last_name",
            "user__phone",
            "user__is_verify_phone",
            "user__email",
            "image__image",
            "created_at",
            "updated_at",
            "disable_account"
        )
        return Passenger.objects.filter(
            user_id=self.request.user.id
        ).select_related(
            "user",
            "image"
        ).only(*fields).annotate(
            all_trip_count=Count("passenger_trips")
        )


class UpdateUserView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def patch(self, request, *args, **kwargs):
        query = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(query, data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(success=True, error=False, result=serializer.data)


class VerifyRequestVerifiedPhoneView(AsyncAPIView):
    """
    تایید شماره همراه
    """
    serializer_class = VerifyRequestVerifiedPhoneSerializer

    async def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        # cache key
        ip = get_client_ip(request)
        redis_key = f"otp_{phone}_{ip}_{code}"

        # get in redis
        get_redis_key = await cache.aget(redis_key)
        if get_redis_key is None:
            return response(
                success=False,
                result={},
                error="کد اشتباه هست یا منقضی شده هست",
                status_code=404
            )

        try:
            # get user
            user = await User.objects.filter(
                is_active=True,
                phone=phone,
            ).only("id", "is_verify_phone", "is_staff", "is_passenger", "is_active").afirst()

            if not user:
                raise NotFound("حساب کاربری پیدا نشد")

            # check is_verify phone
            if user.is_verify_phone:
                raise AccountIsVerified()

            # update user
            await User.objects.filter(id=user.id).aupdate(is_verify_phone=True)

            # remove redis key
            await cache.adelete(redis_key)

            token = await sync_to_async(lambda: RefreshToken.for_user(user))()

            iran_timezone = pytz_timezone("Asia/Tehran")
            expire_timestamp = int(time.time()) + SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].seconds
            expire_date = datetime.datetime.fromtimestamp(expire_timestamp, tz=iran_timezone)

            data = {
                "mobile": phone,
                "is_staff": user.is_staff,
                "is_verify_phone": True,
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

        except (NotFound, AccountIsVerified) as e:
            await cache.adelete(redis_key)  # remove otp when raise exception
            raise e


class CarBrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    دریافت لیست برندهای خودرو
    """
    serializer_class = CarBrandSerializer
    permission_classes = (IsAuthenticated,)
    queryset = CarBrand.objects.filter(is_active=True)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ['brand_name']
    ordering_fields = ['brand_name', 'created_at']
    ordering = ('brand_name',)


class CarModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    دریافت لیست مدل‌های خودرو
    می‌توانید با پارامتر brand=id فیلتر کنید
    """
    serializer_class = CarModelSerializer
    permission_classes = (IsAuthenticated,)
    queryset = CarModel.objects.filter(is_active=True).select_related('brand')
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('brand',)
    search_fields = ('model_name', 'brand__brand_name')
    ordering_fields = ('model_name', 'brand__brand_name', 'created_at')
    ordering = ('brand__brand_name', 'model_name')
