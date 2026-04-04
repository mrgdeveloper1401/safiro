from adrf.serializers import Serializer as AdrfSerializer
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apis.v1.utils.custom_exceptions import (
    PasswordNotMathException,
    OldPasswordNotMathException,
    NationCodeAlreadyExistsException,
    LicenseNumberAlreadyExistsException,
    DriverAlreadyExistsException
)
from apps.auth_app.models import UserNotification, Driver, Image, DriverDocument, User, Passenger, Car, DriverCar
from apps.auth_app.validators import PhoneNumberValidator


class RequestOtpSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=(PhoneNumberValidator(),))


class OtpVerifySerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=(PhoneNumberValidator(),))
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


class SimpleCarSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.brand_name")
    model = serializers.CharField(source="model.model_name")

    class Meta:
        model = Car
        fields = ("name", "brand", "model", "year")


class DriverSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.only("id").filter(is_active=True),
    )

    class Meta:
        model = Driver
        fields = (
            "id",
            "image",
            "nation_code",
            "father_name",
            "license_number",
            "verification_status",
            "disable_account"
        )
        extra_kwargs = {
            "verification_status": {"read_only": True},
            "disable_account": {"read_only": True},
            "is_active": {"read_only": True},
            "nation_code": {"required": True},
            "license_number": {"read_only": True},
        }

    def validate_image(self, data):
        user_id = self.context['request'].user.id
        owner_image = Image.objects.only("id").filter(id=data.id, created_by_id=user_id, is_active=True)
        if not owner_image.exists():
            raise NotFound("image not found")
        return data

    def create(self, validated_data):
        try:
            user_id = self.context['request'].user.id
            return Driver.objects.create(user_id=user_id, **validated_data)
        except IntegrityError as e:
            error_ms = str(e)
            if "nation_code" in error_ms:
                raise NationCodeAlreadyExistsException()

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as e:
            error_ms = str(e)
            if "nation_code" in error_ms:
                raise NationCodeAlreadyExistsException()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.get_image_url if instance.image else None
        # data['car'] = SimpleCarSerializer(instance.car).data if instance.car else None
        data['user'] = UserInfoSerializer(instance.user).data
        return data


class DriverCarSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(
        queryset=Car.objects.only("id").filter(is_active=True),
    )

    class Meta:
        model = DriverCar
        exclude = ("is_active",)
        read_only_fields = ("driver",)

    def create(self, validated_data):
        driver_pk = self.context['driver_pk']
        user_id = self.context['request'].user.id

        # check driver_pk
        if not Driver.objects.filter(id=driver_pk, user_id=user_id).exists():
            raise NotFound("driver not found")
        return DriverCar.objects.create(driver_id=int(driver_pk), **validated_data)


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "username",
            "email",
            "is_verify_phone",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "phone": {'read_only': True},
            "is_verify_phone": {'read_only': True},
        }


class PassengerSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.only("id").filter(is_active=True),
    )

    class Meta:
        model = Passenger
        fields = '__all__'
        extra_kwargs = {
            "user": {"read_only": True},
            "disable_account": {"read_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserPassengerSerializer(instance.user).data
        return data

    def validate(self, attrs):
        image = attrs.get('image', None)
        if image:
            # check image
            user_id = self.context['request'].user.id
            check_img = Image.objects.filter(id=image.id, is_active=True, created_by_id=user_id).only("id")
            if not check_img.exists():
                raise NotFound("image not found")
        return attrs


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
        if not Image.objects.filter(
            is_active=True,
            id=data.id,
            created_by_id=user_id
        ).exists():
            raise NotFound("عکس مربوطه پیدا نشد")
        return data

    def create(self, validated_data):
        user_id = self.context['request'].user.id

        # check driver profile
        driver = Driver.objects.filter(user_id=user_id).only("id")
        if not driver.exists():
            raise NotFound("راننده پیدا نشد")

        # create driver doc
        driver_profile = driver.first()
        return DriverDocument.objects.create(
            driver_id=driver_profile.pk,
            **validated_data
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.get_image_url
        return data


class SignUpByPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=(PhoneNumberValidator(),))
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


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","is_driver", "is_passenger", "phone")
        extra_kwargs = {
            "is_passenger": {"read_only": True},
            "phone": {"read_only": True}
        }

    def update(self, instance, validated_data):
        up = super().update(instance, validated_data)
        if instance.is_driver:
            Driver.objects.create(user_id=instance.id)
        return up


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")
