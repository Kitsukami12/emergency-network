import random
import statistics
import time

from app.core.config import AMBULANCE_SEED
from app.core.seeds import load_ambulances
from app.services.astar import route_between
from app.services.routing import get_graph
from app.services.traffic import tomtom_route

rng = random.Random(7)
G = get_graph()
nodes = list(G.nodes)
ambs = load_ambulances(AMBULANCE_SEED)

pairs = []
for _ in range(20):
    a = rng.choice(ambs)
    n = rng.choice(nodes)
    lat, lon = G.nodes[n]["y"], G.nodes[n]["x"]
    mine = route_between(a.location.lat, a.location.lon, lat, lon)
    live = tomtom_route(a.location.lat, a.location.lon, lat, lon)
    time.sleep(0.3)                     # stay under TomTom's per-second limit
    if mine and live:
        pairs.append((mine["estimated_time_min"], live["estimated_time_min"]))

static = [p[0] for p in pairs]
live = [p[1] for p in pairs]
print(f"{len(pairs)} routes")
print(f"mean static A*: {statistics.mean(static):.1f} min")
print(f"mean TomTom   : {statistics.mean(live):.1f} min")
print(f"static / live ratio: {statistics.mean(s / l for s, l in pairs):.2f}")
print(f"mean absolute error: {statistics.mean(abs(s - l) for s, l in pairs):.1f} min")