import httpx
from decouple import config

from base.utils.custom_exceptions import a_request_error

NESHAN_API_KEY = config("NESHAN_MAP_API_KEY", cast=str)
NESHAN_ROUTING_URL = config("NESHAN_ROUTING_URL", cast=str)
NESHAN_ROUTER_NO_TRAFFIC = config("NESHAN_ROUTER_NO_TRAFFIC", cast=bool)

COMMON_HEADERS = {
    "Api-Key": NESHAN_API_KEY,
}


@a_request_error
async def routing_with_traffic(
    car_type,
    origin,
    destination,
    use_traffic: bool = True,
    alternative=True,
    avoid_traffic_zone=False,
    avoid_odd_even_zone=False,
):
    """
    سرویس مسیریابی  با ترافیک (Routing API)
    سرویس مسیریابی بدون ترافیک (noTraffic Routing API)
    """
    params = {
        "type": car_type,
        "origin": origin,
        "destination": destination,
        "alternative": alternative,
        "avoidTrafficZone": avoid_traffic_zone,
        "avoidOddEvenZone": avoid_odd_even_zone,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        if use_traffic:
            response = await client.get(
                url=NESHAN_ROUTING_URL, headers=COMMON_HEADERS, params=params
            )
        else:
            response = await client.get(
                url=NESHAN_ROUTER_NO_TRAFFIC, headers=COMMON_HEADERS, params=params
            )
        return response.json()
