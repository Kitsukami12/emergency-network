import os

import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["TOMTOM_API_KEY"]

TRIPS = {
    "Apollo -> Rajwada area": ((22.7586, 75.8889), (22.7196, 75.8577)),
    "Vijay Nagar -> Airport": ((22.7533, 75.8937), (22.7218, 75.8011)),
}

for label, ((a_lat, a_lon), (b_lat, b_lon)) in TRIPS.items():
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{a_lat},{a_lon}:{b_lat},{b_lon}/json"
    r = requests.get(url, params={"key": KEY, "traffic": "true", "travelMode": "car",
                                  "routeType": "fastest", "computeTravelTimeFor": "all"})
    if r.status_code != 200:
        print(label, "FAILED", r.status_code, r.text[:300])
        continue
    s = r.json()["routes"][0]["summary"]
    print(f"{label}: {s['lengthInMeters']/1000:.1f} km, "
          f"{s['travelTimeInSeconds']/60:.1f} min with traffic, "
          f"{s.get('noTrafficTravelTimeInSeconds', 0)/60:.1f} min without, "
          f"delay {s.get('trafficDelayInSeconds', 0)/60:.1f} min")