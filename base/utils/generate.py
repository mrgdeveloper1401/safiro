import secrets
import string

def generate_otp(length=6):
    """OTP امن 6 رقمی"""
    digits = string.digits  # '0123456789'
    return ''.join(secrets.choice(digits) for _ in range(length))
