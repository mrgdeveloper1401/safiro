from django.utils import timezone
from uuid_extension import uuid7


def uuid_7_timestamp():
    current_time = timezone.now().timestamp()
    uuid_7 = uuid7(current_time)
    return uuid_7
