from django.core.validators import RegexValidator


class PhoneNumberValidator(RegexValidator):
    message = "شماره تماس باید بین ۹ رقم یا ۱۵ رقم باشد و به صورت عددی باشد"
    regex = r"\d{9,15}$"
