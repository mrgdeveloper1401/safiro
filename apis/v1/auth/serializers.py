from adrf.serializers import Serializer
from rest_framework import serializers

from auth_app.models import UserNotification, Driver, Image, DriverDocument
from auth_app.validators import PhoneNumberValidator


class RequestOtpSerializer(Serializer):
    mobile_phone = serializers.CharField()


class OtpVerifySerializer(Serializer):
    mobile_phone = serializers.CharField()
    otp = serializers.CharField()


class LoginPhonePasswordSerializer(Serializer):
    phone = serializers.CharField()
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


class DriverSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.only("id").filter(is_active=True),
    )

    class Meta:
        model = Driver
        fields = (
            "id",
            "first_name",
            "last_name",
            "image",
            "nation_code",
            "father_name",
            "license_number",
            "verification_status"
        )
        extra_kwargs = {
            "verification_status": {"read_only": True},
        }
    def validate_image(self, data):
        user_id = self.context['request'].user.id
        owner_image = Image.objects.only("id").filter(id=data.id, created_by_id=user_id, is_active=True)
        if not owner_image.exists():
            raise serializers.ValidationError("image not found")
        return data

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        return Driver.objects.create(user_id=user_id, **validated_data)


class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = (
            "id",
            "image"
        )

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        return Image.objects.create(created_by_id=user_id, **validated_data)


class DriverDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverDocument
        fields = (
            "id",
            "doc_type",
            "is_verified",
            "verifier_note"
        )
        extra_kwargs = {
            "is_verified": {"read_only": True},
            "verifier_note": {'read_only': True}
        }


class SignUpByPhoneSerializer(Serializer):
    phone = serializers.CharField(validators=[PhoneNumberValidator()])
    password = serializers.CharField()
    confirm_password = serializers.CharField()


class LoginByPhoneSerializer(Serializer):
    phone = serializers.CharField(validators=(PhoneNumberValidator(),))
    password = serializers.CharField()
