import os
import time

import requests
from dotenv import load_dotenv

from app.services.astar import route_between

load_dotenv()
KEY = os.getenv("TOMTOM_API_KEY")
BASE = "https://api.tomtom.com/routing/1/calculateRoute"
CACHE_TTL_S = 120          # reuse a result for 2 minutes: saves the daily free quota
_cache = {}


def tomtom_route(lat1, lon1, lat2, lon2):
    """Live-traffic route from TomTom, in the same shape as route_between.
    Returns None on any failure (no key, network error, quota exceeded)."""
    if not KEY:
        return None
    ck = (round(lat1, 4), round(lon1, 4), round(lat2, 4), round(lon2, 4))
    hit = _cache.get(ck)
    if hit and time.time() - hit[0] < CACHE_TTL_S:
        return hit[1]
    try:
        r = requests.get(
            f"{BASE}/{lat1},{lon1}:{lat2},{lon2}/json",
            params={"key": KEY, "traffic": "true", "travelMode": "car",
                    "routeType": "fastest", "computeTravelTimeFor": "all"},
            timeout=5)
        r.raise_for_status()
        route = r.json()["routes"][0]
        s = route["summary"]
        points = route["legs"][0]["points"]
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None
    out = {
        "distance_km": round(s["lengthInMeters"] / 1000, 2),
        "estimated_time_min": round(s["travelTimeInSeconds"] / 60, 1),
        "no_traffic_time_min": round(
            s.get("noTrafficTravelTimeInSeconds", s["travelTimeInSeconds"]) / 60, 1),
        "route": [[p["latitude"], p["longitude"]] for p in points],
        "source": "tomtom_live",
    }
    _cache[ck] = (time.time(), out)
    return out


def best_route(lat1, lon1, lat2, lon2):
    """Live traffic when available, otherwise your own static A*, clearly labelled."""
    result = tomtom_route(lat1, lon1, lat2, lon2)
    if result:
        return result
    result = route_between(lat1, lon1, lat2, lon2)
    if result:
        result["source"] = "static_astar"
    return result