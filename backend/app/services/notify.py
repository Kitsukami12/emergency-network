from app.core import db
from app.core.schemas import Accident
from app.services.assignment import times_from
from app.services.routing import snap_to_node

_node_cache: dict[str, int] = {}


def _hospital_node(h: dict) -> int:
    if h["hospital_id"] not in _node_cache:
        _node_cache[h["hospital_id"]] = snap_to_node(h["lat"], h["lon"])
    return _node_cache[h["hospital_id"]]


def nearest_hospital(lat: float, lon: float):
    """Nearest major hospital by road time from the scene. Falls back to any hospital.
    ASSUMPTION: no data on trauma capability, so 'major' is a name-based guess."""
    hospitals = db.list_hospitals()
    pool = [h for h in hospitals if h["is_major"]] or hospitals
    times = times_from(snap_to_node(lat, lon))
    best = None
    for h in pool:
        t = times.get(_hospital_node(h))
        if t is not None and (best is None or t < best[0]):
            best = (t, h)
    return (best[1], round(best[0] / 60, 1)) if best else (None, None)


def build_payload(acc: Accident, hospital: dict, eta_min: float) -> dict:
    return {
        "accident_id": acc.accident_id,
        "location": {"lat": acc.location.lat, "lon": acc.location.lon},
        "severity_estimate": acc.severity.value,
        "severity_confidence": acc.severity_confidence,
        "detection_confidence": acc.detection_confidence,
        "vehicles_involved": acc.vehicle_count,
        "camera_id": acc.camera_id,
        "frame_path": acc.frame_path,
        "detected_at": acc.detected_at.isoformat() if acc.detected_at else None,
        "weather": acc.weather.model_dump() if acc.weather else None,
        "scene_to_hospital_min": eta_min,
        "hospital": hospital["name"],
        "note": "Automated estimate from a prototype. Verify before acting.",
    }


def notify_nearest(acc: Accident):
    hospital, eta = nearest_hospital(acc.location.lat, acc.location.lon)
    if hospital is None:
        return None
    return db.add_notification(acc.accident_id, hospital["hospital_id"],
                               build_payload(acc, hospital, eta))