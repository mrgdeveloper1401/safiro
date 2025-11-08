from rest_framework.exceptions import APIException


class AuthenticationFailed(APIException):
    status_code = 403
    default_detail = 'کاربر احراز هویت شده نمیتواند دسترسی پیدا کند'
    default_code = 11


class TimeOutException(APIException):
    status_code = 400
    default_detail = "زمان درخواست بیش از حد طول کشیده شده هست لطفا دروباره درخواست بدید"
    default_code = 1


class ConnectionErrorException(APIException):
    status_code = 400
    default_detail = "مشکل  در برقراری ارتباط با سرور"
    default_code = 2


class NetworkErrorException(APIException):
    status_code = 400
    default_detail = "شبکه ای که در ان هستید قادر به برقرای ارتباط با سرور نیست"
    default_code = 3


class HttpStatusException(APIException):
    status_code = 400
    default_detail = "کد خطای غیر منتظره"
    default_code = 4
