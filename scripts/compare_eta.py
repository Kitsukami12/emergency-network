import argparse
import csv
import random
import statistics
import time
from datetime import datetime
from pathlib import Path

from app.core.config import AMBULANCE_SEED
from app.core.seeds import load_ambulances
from app.services.astar import route_between
from app.services.routing import get_graph
from app.services.traffic import tomtom_route

p = argparse.ArgumentParser()
p.add_argument("--n", type=int, default=20)
args = p.parse_args()

rng = random.Random()                      # unseeded: new routes each run
G = get_graph()
nodes = list(G.nodes)
ambs = load_ambulances(AMBULANCE_SEED)

out = Path("results/eta_samples.csv")
out.parent.mkdir(exist_ok=True)
new_file = not out.exists()
rows = []
with out.open("a", newline="") as f:
    w = csv.writer(f)
    if new_file:
        w.writerow(["timestamp", "hour", "km", "static_min", "tomtom_free_min", "tomtom_live_min"])
    for _ in range(args.n):
        a = rng.choice(ambs)
        n = rng.choice(nodes)
        lat, lon = G.nodes[n]["y"], G.nodes[n]["x"]
        mine = route_between(a.location.lat, a.location.lon, lat, lon)
        live = tomtom_route(a.location.lat, a.location.lon, lat, lon)
        time.sleep(0.3)
        if mine and live:
            now = datetime.now()
            row = [now.isoformat(timespec="minutes"), now.hour, live["distance_km"],
                   mine["estimated_time_min"], live["no_traffic_time_min"],
                   live["estimated_time_min"]]
            w.writerow(row)
            rows.append(row)

s = [r[3] for r in rows]; free = [r[4] for r in rows]; live = [r[5] for r in rows]
print(f"{len(rows)} routes at hour {datetime.now().hour}")
print(f"static / TomTom-free : {statistics.mean(a / b for a, b in zip(s, free)):.2f}   (your speed model)")
print(f"TomTom-free / live   : {statistics.mean(a / b for a, b in zip(free, live)):.2f}   (real traffic effect)")
print(f"static / TomTom-live : {statistics.mean(a / b for a, b in zip(s, live)):.2f}   (total)")