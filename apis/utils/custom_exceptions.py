from rest_framework.exceptions import APIException


class AuthenticationFailed(APIException):
    status_code = 403
    default_detail = "کاربر احراز هویت شده نمیتواند دسترسی پیدا کند"
    default_code = "permission_denied"


class TimeOutException(APIException):
    status_code = 400
    default_detail = (
        "زمان درخواست بیش از حد طول کشیده شده هست لطفا دروباره درخواست بدید"
    )
    default_code = "to_many_requests"


class ConnectionErrorException(APIException):
    status_code = 400
    default_detail = "مشکل  در برقراری ارتباط با سرور"
    default_code = "connection_error"


class NetworkErrorException(APIException):
    status_code = 400
    default_detail = "شبکه ای که در ان هستید قادر به برقرای ارتباط با سرور نیست"
    default_code = "network_error"


class HttpStatusException(APIException):
    status_code = 400
    default_detail = "کد خطای غیر منتظره"
    default_code = "invalid_request"


class UserExistsException(APIException):
    status_code = 400
    default_detail = "کاربر از قبل وجود دارد میتواند به حساب خود وارد شود"
    default_code = "user_exists"


class PasswordNotMathException(APIException):
    status_code = 400
    default_detail = "پسورد ها یکی نیستند"
    default_code = "password_not_math"


class OldPasswordNotMathException(APIException):
    status_code = 400
    default_detail = "پسورد قبلی شما با پسورد الان یکی نیست "
    default_code = "old_password_not_math"


class AccountIsVerified(APIException):
    status_code = 400
    default_detail = "حساب شما قبلا تایید شده هست "
    default_code = "account_is_verified"


class NationCodeAlreadyExistsException(APIException):
    status_code = 400
    default_detail = "کد ملی تکراری میباشد"
    default_code = "nation_code_already_exists"


class LicenseNumberAlreadyExistsException(APIException):
    status_code = 400
    default_detail = "شماره پلاک تکراری میباشد"
    default_code = "license_number_already_exists"


class DriverAlreadyExistsException(APIException):
    status_code = 400
    default_detail = "شما قبلا پروفایل راننده ایجاد کرده‌اید"
    default_code = "driver_already_exists"


class NotActiveAccount(APIException):
    status_code = 403
    default_code = "not_active_account"
    default_detail = "حساب شما مسدود میباشد برای پیگیری با واحد پشتیبانی تماس بگیرید"


class NotDriverException(APIException):
    status_code = 403
    default_code = "not_driver"
    default_detail = (
        "شما حساب راننده رو ندارید اگه تمایل به فعال سازی میتوانید ان را درخواست بدید"
    )


class RequestOtpType(APIException):
    status_code = 400
    default_code = "request_otp_type"
    default_detail = "نوع درخواست کد اعتبار سنحی بین (otp, forget_password) باشه"
