from adrf.serializers import Serializer as AdrfSerializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apis.v1.utils.custom_exceptions import PasswordNotMathException, OldPasswordNotMathException
from auth_app.models import UserNotification, Driver, Image, DriverDocument, User
from auth_app.validators import PhoneNumberValidator


class RequestOtpSerializer(AdrfSerializer):
    mobile_phone = serializers.CharField()


class OtpVerifySerializer(AdrfSerializer):
    mobile_phone = serializers.CharField()
    otp = serializers.CharField()


class LoginPhonePasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(
        validators=(
            PhoneNumberValidator(),
        )
    )
    password = serializers.CharField()


class VerifyForgetPassword(AdrfSerializer):
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
            raise NotFound("image not found")
        return data

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        return Driver.objects.create(user_id=user_id, **validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = str(instance.image.get_image_url)
        return data


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
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.only("id").filter(is_active=True),
    )

    class Meta:
        model = DriverDocument
        fields = (
            "id",
            "doc_type",
            "image",
            "is_verified",
            "verifier_note"
        )
        extra_kwargs = {
            "is_verified": {"read_only": True},
            "verifier_note": {'read_only': True}
        }

    def validate_image(self, data):
        user_id = self.context['request'].user.id
        img = Image.objects.filter(
            is_active=True,
            id=data.id,
            created_by_id=user_id
        ).order_by("id")
        if not img.exists():
            raise NotFound("عکس مربوطه پیدا نشد")
        return data

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        # check driver profile
        driver_profile = Driver.objects.filter(user_id=user_id, is_active=True).only("id")
        if not driver_profile.exists():
            raise NotFound("راننده پیدا نشد")
        # create driver doc
        return DriverDocument.objects.create(
            profile_id=driver_profile.first().id,
            **validated_data
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.get_image_url
        return data


# class SignUpByPhoneSerializer(AdrfSerializer):
#     phone = serializers.CharField(validators=[PhoneNumberValidator()])
#     password = serializers.CharField()
#     confirm_password = serializers.CharField()


class SignUpByPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[PhoneNumberValidator()])
    password = serializers.CharField()
    confirm_password = serializers.CharField()


class LoginByPhoneSerializer(AdrfSerializer):
    phone = serializers.CharField(validators=(PhoneNumberValidator(),))
    password = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        old_password = attrs.get("old_password")
        user_id = self.context['request'].user.id

        # check new password
        if new_password != confirm_password:
            raise PasswordNotMathException()
        else:
            # get user
            user = User.objects.filter(id=user_id, is_active=True).only("password")
            get_user = user.first()

            # check old password
            if not get_user.check_password(old_password):
                raise OldPasswordNotMathException()
            else:
                # update password
                user.update(password=new_password)
        return attrs


class RequestLogVerifyPhoneSerializer(AdrfSerializer):
    phone = serializers.CharField(
        validators=(
            PhoneNumberValidator(),
        )
    )


class VerifyRequestVerifiedPhoneSerializer(AdrfSerializer):
    phone = serializers.CharField(
        validators=(
            PhoneNumberValidator(),
        )
    )
    code = serializers.CharField()


class UserStatusSerializer(serializers.Serializer):
    is_driver = serializers.BooleanField(required=False)
    is_passenger = serializers.BooleanField(required=False)
