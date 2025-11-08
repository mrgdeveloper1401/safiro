from typing import Union

from rest_framework.response import Response


def response(success: bool, result: Union[dict, list] = None, error: Union[str, bool] = None, status_code: int = 200):
    data = {
        "success": success,
        "result": result,
        "error": error
    }
    return Response(data, status=status_code)
