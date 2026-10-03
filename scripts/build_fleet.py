import json
import math
from pathlib import Path

SRC = Path("data/seeds/hospitals.json")
OUT_HOSPITALS = Path("data/seeds/hospitals_clean.json")
OUT_AMBULANCES = Path("data/seeds/ambulances.json")
N_BASES = 25
DEDUPE_M = 120

# Names containing these are not emergency destinations.
NOT_EMERGENCY = ("clinic", "ayurved", "homeo", "lasik", "laser", "netra", "eye", "dental",
                 "skin", "ivf", "diagnostic", "investigation", "pathology", "laborator",
                 "swasth kendra", "physio", "healthcare", "dhootapapeshwar", "voluntary",
                 "store", "medical hall", "medicals", "pharmacy", "chemist", "medico",
                 "medical care")
# Names containing these look like large hospitals.
MAJOR = ("district hospital", "medical college", "medical sciences", "medical scinces",
         "institute", "super speciality", "superspeciality", "multispeciality",
         "multi speciality", "trauma", "apollo", "medanta", "bombay", "choithram",
         "shalby", "jupiter", "trust", "research centre", "research center")


def dist_m(a, b):
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dl = math.radians(b["lon"] - a["lon"])
    x = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(x))


def spread(pool, chosen, k):
    """Greedily add the pool point farthest from everything chosen so far."""
    chosen = list(chosen)
    pool = [p for p in pool if p not in chosen]
    while pool and len(chosen) < k:
        best = pool[0] if not chosen else max(
            pool, key=lambda p: min(dist_m(p, c) for c in chosen))
        chosen.append(best)
        pool.remove(best)
    return chosen


raw = json.loads(SRC.read_text())

# 1. name filter
candidates = []
for h in raw:
    low = h["name"].strip().lower()
    if low.startswith("dr") or any(k in low for k in NOT_EMERGENCY):
        continue
    h["is_major"] = h["has_emergency"] or any(k in low for k in MAJOR)
    candidates.append(h)

# 2. de-duplicate by location, keeping major hospitals first
candidates.sort(key=lambda h: not h["is_major"])
clean = []
for h in candidates:
    if all(dist_m(h, k) > DEDUPE_M for k in clean):
        clean.append(h)
for i, h in enumerate(clean, 1):
    h["hospital_id"] = f"H{i:03d}"
OUT_HOSPITALS.write_text(json.dumps(clean, indent=2))

# 3. ambulance bases: spread-out majors first, then fill from the rest
major = [h for h in clean if h["is_major"]]
bases = spread(major, [], N_BASES)
bases = spread(clean, bases, N_BASES)

ambulances = []
for b in bases:
    for _ in range(2 if b["is_major"] else 1):   # ASSUMPTION: 2 at major hospitals, 1 elsewhere
        ambulances.append({"ambulance_id": f"A{len(ambulances) + 1:02d}",
                           "base_name": b["name"], "lat": b["lat"], "lon": b["lon"]})
OUT_AMBULANCES.write_text(json.dumps(ambulances, indent=2))

print(f"{len(raw)} raw -> {len(clean)} destination hospitals ({len(major)} major)")
print(f"{len(bases)} ambulance bases, {len(ambulances)} ambulances")
for b in bases:
    print("  ", b["name"], "(major)" if b["is_major"] else "")