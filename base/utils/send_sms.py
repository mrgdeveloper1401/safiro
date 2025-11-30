import httpx
from decouple import config

from .custom_exceptions import request_error

BASE_URL = config('SMS_KAVE_BASE_URL', cast=str, default='https://api.kavenegar.com/v1/')
API_KEY = config("SMS_KAVE_API_KEY", cast=str, default='hello_world!')
KV_PATTERN_NAME_SEND_OTP = config("KV_PATTERN_NAME_SEND_OTP", cast=str, default="hello_world")
SEND_SMS_LOOKUP_URL = BASE_URL + API_KEY + '/verify/lookup.json'

@request_error
async def send_sms(phone: str, code: str):
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "receptor": phone,
        "token": code,
        "template": KV_PATTERN_NAME_SEND_OTP,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=SEND_SMS_LOOKUP_URL,
            params=params,
            timeout=10,
            headers=headers,
        )
        return response.json()


# async def main():
#     sms = await send_sms(phone="09391640664", code="123456")
#     return sms
