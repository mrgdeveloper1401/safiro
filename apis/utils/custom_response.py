from typing import Union

from rest_framework.response import Response


def response(success: bool = True, result: Union[dict, list] = None, error: Union[str, bool] = False, status_code: int = 200):
    data = {
        "success": success,
        "result": result,
        "error": error
    }
    return Response(data, status=status_code)
