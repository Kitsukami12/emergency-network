"""
Checks every ambulance base against the saved Indore road graph.
Run from the project root:  python scripts/check_ambulances.py
"""
import json
import math

import osmnx as ox

GRAPH_FILE = "data/graph/indore.graphml"
SEED_FILE = "data/seeds/ambulances.json"
WARN_M = 1000  # flag anything farther than this from a road junction


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


G = ox.load_graphml(GRAPH_FILE)
nodes = [(n, d["y"], d["x"]) for n, d in G.nodes(data=True)]

lats = [y for _, y, _ in nodes]
lons = [x for _, _, x in nodes]
print(f"Map boundary: lat {min(lats):.4f} to {max(lats):.4f}, "
      f"lon {min(lons):.4f} to {max(lons):.4f}\n")

ambulances = json.load(open(SEED_FILE))
problems = 0
for a in ambulances:
    best = min(nodes, key=lambda n: haversine_m(a["lat"], a["lon"], n[1], n[2]))
    dist = haversine_m(a["lat"], a["lon"], best[1], best[2])
    flag = "  <-- CHECK" if dist > WARN_M else ""
    if flag:
        problems += 1
    print(f'{a["ambulance_id"]}  {a["base_name"][:28]:28}  nearest junction {dist:6.0f} m{flag}')

print(f"\n{problems} ambulance(s) flagged.")