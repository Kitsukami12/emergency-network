import time

import requests

from app.core.schemas import Weather

_cache = {}
CACHE_TTL_S = 600     # weather barely changes in 10 minutes


def _describe(code):
    if code is None:
        return None
    if code == 0:
        return "clear"
    if code in (1, 2, 3):
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if 51 <= code <= 57:
        return "drizzle"
    if 61 <= code <= 67 or 80 <= code <= 82:
        return "rain"
    if 95 <= code <= 99:
        return "thunderstorm"
    return "other"


def get_weather(lat, lon) -> Weather | None:
    """Current weather at a point. Returns None if the service is unreachable."""
    ck = (round(lat, 2), round(lon, 2))
    hit = _cache.get(ck)
    if hit and time.time() - hit[0] < CACHE_TTL_S:
        return hit[1]
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,precipitation,weather_code,visibility,wind_speed_10m",
        }, timeout=5)
        r.raise_for_status()
        c = r.json()["current"]
    except (requests.RequestException, KeyError, ValueError):
        return None
    w = Weather(temperature_c=c.get("temperature_2m"),
                precipitation_mm=c.get("precipitation"),
                visibility_m=c.get("visibility"),
                wind_kph=c.get("wind_speed_10m"),
                weather_code=c.get("weather_code"),
                summary=_describe(c.get("weather_code")))
    _cache[ck] = (time.time(), w)
    return w