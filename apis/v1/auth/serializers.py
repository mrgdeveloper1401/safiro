from adrf.serializers import Serializer
from rest_framework import serializers


class RequestOtpSerializer(Serializer):
    mobile_phone = serializers.CharField()


class OtpVerifySerializer(Serializer):
    mobile_phone = serializers.CharField()
    otp = serializers.CharField()


class LoginPhonePasswordSerializer(Serializer):
    phone = mobile_phone = serializers.CharField()
    password = serializers.CharField()
