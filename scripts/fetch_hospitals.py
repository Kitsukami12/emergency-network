import json
from pathlib import Path

import osmnx as ox

CENTER = (22.7196, 75.8577)   # same centre and radius as the road graph
RADIUS_M = 10000
OUT = Path("data/seeds/hospitals.json")

gdf = ox.features.features_from_point(CENTER, tags={"amenity": "hospital"}, dist=RADIUS_M)
gdf = gdf.reset_index()
points = gdf.geometry.representative_point()   # polygons -> one point

rows, unnamed = [], 0
for (_, r), p in zip(gdf.iterrows(), points):
    name = r.get("name")
    if not isinstance(name, str):
        unnamed += 1
        continue
    kind = r.get("element", r.get("element_type"))
    oid = r.get("id", r.get("osmid"))
    rows.append({
        "hospital_id": f"H{len(rows) + 1:03d}",
        "name": name,
        "lat": round(p.y, 6),
        "lon": round(p.x, 6),
        "osm_id": f"{kind}/{oid}",
        "has_emergency": str(r.get("emergency", "")).lower() == "yes",
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=2))
print(f"saved {len(rows)} named hospitals ({unnamed} unnamed skipped)")
print(f"{sum(h['has_emergency'] for h in rows)} are tagged emergency=yes")