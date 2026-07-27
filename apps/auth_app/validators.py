from django.core.validators import RegexValidator


class PhoneNumberValidator(RegexValidator):
    message = "شماره تماس باید 11 رقم باشد و به صورت عددی باشد"
    regex = r"\d{11}$"
