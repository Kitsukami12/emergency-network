from app.core import db
from app.services import notify


def test_nearest_hospital_picks_lowest_road_time(monkeypatch):
    notify._node_cache.clear()
    hospitals = [{"hospital_id": f"H{i}", "name": f"Hosp {i}", "lat": float(i),
                  "lon": 0.0, "is_major": True} for i in (1, 2, 3)]
    monkeypatch.setattr(db, "list_hospitals", lambda: hospitals)
    monkeypatch.setattr(notify, "snap_to_node", lambda lat, lon: int(lat))   # node id = lat
    monkeypatch.setattr(notify, "times_from", lambda node: {1: 600, 2: 120, 3: 300})
    h, eta = notify.nearest_hospital(0.5, 0.0)
    assert h["hospital_id"] == "H2" and eta == 2.0