from django.core.validators import RegexValidator


class PhoneNumberValidator(RegexValidator):
    message = "Enter a valid phone number. phone number must be digit and between 9 or 15 digits."
    regex = r"\d{9,15}$"
