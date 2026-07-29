import httpx

from apis.utils.custom_exceptions import (
    TimeOutException,
    ConnectionErrorException,
    NetworkErrorException,
    HttpStatusException,
)


def request_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except httpx.TimeoutException:
            raise TimeOutException()
        except httpx.ConnectError:
            raise ConnectionErrorException()
        except httpx.NetworkError:
            raise NetworkErrorException()
        except Exception as e:
            raise HttpStatusException(detail=str(e))

    return wrapper


def a_request_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.TimeoutException:
            raise TimeOutException()
        except httpx.ConnectError:
            raise ConnectionErrorException()
        except httpx.NetworkError:
            raise NetworkErrorException()
        except Exception as e:
            raise HttpStatusException(detail=str(e))

    return wrapper
