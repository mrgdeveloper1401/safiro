import json

import httpx
from decouple import config

from base.utils.custom_exceptions import request_error


NESHAN_SERVICE_API_KEY = config("NESHAN_SERVICE_API_KEY", cast=str)
REVERSE_GEOCODE_TIMEOUT = config("REVERSE_GEOCODE_TIMEOUT", cast=int, default=15)


@request_error
def calc_address_to_x_y(address, state_name, city_name, location: dict[str, float]):
    url = "https://api.neshan.org/geocoding/v1"
    headers = {
        "Api-Key": NESHAN_SERVICE_API_KEY,
        "Content-Type": "application/json",
    }
    request_data = {
        "address": address,
        "province": state_name,
        "city": city_name,
        "location": location,
    }
    json_string = json.dumps(request_data, ensure_ascii=False)

    response = httpx.get(url, params=json_string, headers=headers)
    return response.json()


@request_error
def reverse_geocode(lat, lng):
    """
    تبدیل مختصات به ادرس
    lat = عرض جغرافیایی
    lng = طول جغرافیایی
    :return:
    """
    if not lat or not lng:
        raise ValueError("lat and lng are required")
    url = "https://api.neshan.org/v5/reverse"
    headers = {
        "Api-Key": NESHAN_SERVICE_API_KEY,
    }
    params = {
        "lat": lat,
        "lng": lng,
    }
    response = httpx.get(
        url, params=params, headers=headers, timeout=REVERSE_GEOCODE_TIMEOUT
    )
    return response.json()
