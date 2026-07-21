from rest_framework.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    RequestOtpView,
    OtpVerifyView,
    LoginPhonePasswordView,
    UserNotificationView,
    DriverView,
    UploadImageView,
    DriverDocView,
    SignUpByPhoneView,
    UserTypeViewSet,
    PassengerViewSet,
    UpdateUserView,
    DriverCarViewSet,
    CarBrandViewSet,
    CarModelViewSet
)

app_name = "v1_auth"

router = SimpleRouter()
router.register("user_notification", UserNotificationView, basename="user_notification")
router.register("driver", DriverView, basename="driver")
router.register("passenger", PassengerViewSet, basename="passenger")
router.register('user_type', UserTypeViewSet, basename="user_type")
router.register('car/brand', CarBrandViewSet, basename='car_brand')
router.register('car/model', CarModelViewSet, basename='car_model')

# driver router
driver_router = NestedSimpleRouter(router, r"driver", lookup="driver")
driver_router.register('driver_car', DriverCarViewSet, basename="driver_car")
driver_router.register('driver_doc', DriverDocView, basename="driver_doc")

urlpatterns = [
    path("request_otp_phone/", RequestOtpView.as_view(), name="request_otp_phone"),
    path('verify_otp/', OtpVerifyView.as_view(), name="verify_otp"),
    path("login_phone_password/", LoginPhonePasswordView.as_view(), name="login_phone_password"),
    path("sing_up_by_phone/", SignUpByPhoneView.as_view(), name="signup_by_phone"),
    path("update_user/", UpdateUserView.as_view(), name="update_user"),
    path("upload_image/", UploadImageView.as_view(), name="upload_image"),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
] + router.urls + driver_router.urls
