import secrets
import string
import time
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from base.settings import SIMPLE_JWT


def generate_otp(length=6):
    """OTP امن 6 رقمی"""
    digits = string.digits  # '0123456789'
    return ''.join(secrets.choice(digits) for _ in range(length))


def generate_token(user):
    token = RefreshToken.for_user(user)

    expire_date = timezone.now() + timedelta(days=SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].days)
    refresh_expire_date = timezone.now() + timedelta(days=SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].days)

    return {
        "access_token": str(token.access_token),
        "refresh_token": str(token),
        "jwt": "Bearer",
        "expire_date_access_token": expire_date,
        'access_token_life_time': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        "expire_date_refresh_token": refresh_expire_date
    }
