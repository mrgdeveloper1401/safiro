from rest_framework.urls import path
from .views import (
    RequestOtpView
)

app_name = "v1_auth"

urlpatterns = [
    path("request_otp_phone/", RequestOtpView.as_view(), name="request_otp_phone"),
]
