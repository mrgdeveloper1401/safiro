from adrf.serializers import Serializer
from rest_framework import serializers

from auth_app.models import UserNotification


class RequestOtpSerializer(Serializer):
    mobile_phone = serializers.CharField()


class OtpVerifySerializer(Serializer):
    mobile_phone = serializers.CharField()
    otp = serializers.CharField()


class LoginPhonePasswordSerializer(Serializer):
    phone = mobile_phone = serializers.CharField()
    password = serializers.CharField()


class VerifyForgetPassword(Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    code = serializers.CharField()


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = (
            "id",
            "title",
            "body",
            "created_at",
            "updated_at",
        )
