import httpx
from decouple import config

from .custom_exceptions import request_error

# kavenegra
BASE_URL = config('SMS_KAVE_BASE_URL', cast=str, default='https://api.kavenegar.com/v1/')
API_KEY = config("SMS_KAVE_API_KEY", cast=str, default='hello_world!')
KV_PATTERN_NAME_SEND_OTP = config("KV_PATTERN_NAME_SEND_OTP", cast=str, default="hello_world")
SEND_SMS_LOOKUP_URL = BASE_URL + API_KEY + '/verify/lookup.json'

# sorna
SORNA_USERNAME = config("SORNA_USERNAME", cast=str, default='')
SORNA_PASSWORD = config("SORNA_PASSWORD", cast=str, default='')
SORNA_PORTAL_CODE = config("SORNA_PORTAL_CODE", cast=int, default=1234)
SORNA_BASE_URL = config("SORNA_BASE_URL", cast=str, default='https://api.sorna.com')

# kavenegar
# @request_error
# def send_sms(phone: str, code: str):
#     headers = {
#         "Content-Type": "application/json"
#     }
#     params = {
#         "receptor": phone,
#         "token": code,
#         "template": KV_PATTERN_NAME_SEND_OTP,
#     }
#     response = httpx.post(
#         url=SEND_SMS_LOOKUP_URL,
#         params=params,
#         timeout=10,
#         headers=headers,
#     )
#     return response.json()


@request_error
def send_sms_sorna(phone: str, code: str):
    headers = {
        "Content-Type": "application/json"
    }
    message = f"کد تایید شما برابر است با {code} اگر این درخواست از سمت شما نبوده این پیام رو نادیده بگیرید "
    req_body = {
        "PassWord": SORNA_PASSWORD,
        "UserName": SORNA_USERNAME,
        "PortalCode": SORNA_PORTAL_CODE,
        "Mobile": phone,
        "Message": message,
    }
    sorna_url = "http://sornasms.net/webServiceRest/ServiceSend.svc/SingleSMSEngine"
    response = httpx.post(
        url=sorna_url,
        json=req_body,
        timeout=10,
        headers=headers,
    )
    return response.json()
