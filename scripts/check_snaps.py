from app.core.config import AMBULANCE_SEED
from app.core.seeds import load_ambulances
from app.services.routing import snap_distance_m

for a in load_ambulances(AMBULANCE_SEED):
    d = snap_distance_m(a.location.lat, a.location.lon)
    flag = "  <-- TOO FAR" if d > 500 else ""
    print(f"{a.ambulance_id} {a.base_name} {round(d)} m{flag}")