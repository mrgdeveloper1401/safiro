from rest_framework.urls import path
from .views import (
    RequestOtpView,
    OtpVerifyView,
    LoginPhonePasswordView
)

app_name = "v1_auth"

urlpatterns = [
    path("request_otp_phone/", RequestOtpView.as_view(), name="request_otp_phone"),
    path('verify_otp/', OtpVerifyView.as_view(), name="verify_otp"),
    path("login_phone_password/", LoginPhonePasswordView.as_view(), name="login_phone_password"),
]
