from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]   # project root
GRAPH_FILE = ROOT / "data" / "graph" / "indore.graphml"
AMBULANCE_SEED = ROOT / "data" / "seeds" / "ambulances.json"
LOG_DIR = ROOT / "logs"

# Map boundaries: paste the numbers you just printed
LAT_MIN, LAT_MAX = 22.6297, 22.8095
LON_MIN, LON_MAX = 75.7611, 75.9552

# Duplicate accident rule: same place + same time window = same accident
DEDUPE_RADIUS_M = 100
DEDUPE_WINDOW_MIN = 10

# Detection confidence bands
CONF_ACCEPT = 0.75     # above this: create emergency automatically
CONF_VERIFY = 0.50     # between VERIFY and ACCEPT: human must check