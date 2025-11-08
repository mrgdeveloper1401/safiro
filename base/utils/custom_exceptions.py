import httpx
from rest_framework.exceptions import ValidationError

from apis.v1.utils.custom_exceptions import (
    TimeOutException,
    ConnectionErrorException,
    NetworkErrorException,
    HttpStatusException
)


def request_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.TimeoutException:
            raise TimeOutException()
        except httpx.ConnectError:
            raise ConnectionErrorException()
        except httpx.NetworkError:
            raise NetworkErrorException()
        except httpx.HTTPStatusError:
            raise HttpStatusException()
        except Exception as e:
            raise ValidationError(str(e))
    return wrapper
