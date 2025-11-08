from rest_framework.urls import path
from rest_framework.routers import SimpleRouter
from .views import (
    RequestOtpView,
    OtpVerifyView,
    LoginPhonePasswordView,
    RequestForgetPasswordView,
    VerifyForgetPasswordView,
    UserNotificationView,
    DriverView,
    UploadImageView,
    DriverDocView
)

app_name = "v1_auth"

router = SimpleRouter()
router.register("user_notification", UserNotificationView, basename="user_notification")
router.register("driver", DriverView, basename="driver")
router.register("driver_doc", DriverDocView, basename="driver_doc")

urlpatterns = [
    path("request_otp_phone/", RequestOtpView.as_view(), name="request_otp_phone"),
    path('verify_otp/', OtpVerifyView.as_view(), name="verify_otp"),
    path("login_phone_password/", LoginPhonePasswordView.as_view(), name="login_phone_password"),
    path("request_forget_password/", RequestForgetPasswordView.as_view(), name='request_forget_password'),
    path("verify_forget_password/", VerifyForgetPasswordView.as_view(), name='verify_forget_password'),
    path("upload_image/", UploadImageView.as_view(), name="upload_image"),
] + router.urls
