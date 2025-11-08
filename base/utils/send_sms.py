import httpx
from decouple import config

from base.utils.custom_exceptions import request_error


BASE_URL = config('KAVENEGAR_BASE_URL', cast=str, default='https://api.kavene.io')
VERIFY_URL = BASE_URL + config("KAVENEGAR_VERIFY_URL", cast=str, default='/api/verify')
KV_PATTERN_NAME_SEND_OTP = config("KV_PATTERN_NAME_SEND_OTP", cast=int, default=1234)
API_KEY = config("KAVENEGAR_API_KEY", cast=str, default='hello_world!')


@request_error
async def send_sms(self, phone: str, code: str):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
    }
    params = {
        "receptor": phone,
        "token": code,
        "template": KV_PATTERN_NAME_SEND_OTP,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=VERIFY_URL,
            params=params,
            timeout=10,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
