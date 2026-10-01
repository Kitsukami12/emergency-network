import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
import json
from app.core import config as c

with open(c.AMBULANCE_SEED) as f:
    ambulances = json.load(f)

for amb in ambulances:
    if amb["lat"] < c.LAT_MIN or amb["lat"] > c.LAT_MAX:
        print(f"Warning: Ambulance {amb['ambulance_id']} ({amb['base_name']}) has an invalid latitude.")
    if amb["lon"] < c.LON_MIN or amb["lon"] > c.LON_MAX:
        print(f"Warning: Ambulance {amb['ambulance_id']} ({amb['base_name']}) has an invalid longitude.")

print(f"Checked {len(ambulances)} ambulances")