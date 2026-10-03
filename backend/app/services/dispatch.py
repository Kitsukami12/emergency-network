from app.core import db
from app.core.enums import AccidentStatus, AmbulanceStatus
from app.services.assignment import assign_hungarian, assign_nearest
from app.services.traffic import best_route

STRATEGIES = {"nearest": assign_nearest, "hungarian": assign_hungarian}


def dispatch_pending(strategy: str = "hungarian") -> list[dict]:
    """Match waiting accidents with free ambulances and write the result to the DB."""
    pending = db.list_accidents_by_status(AccidentStatus.AWAITING_AMBULANCE)
    free = [a for a in db.list_ambulances() if a.status == AmbulanceStatus.AVAILABLE]
    if not pending or not free:
        return []

    assignment = STRATEGIES[strategy](free, pending)
    ambs = {a.ambulance_id: a for a in free}
    accs = {a.accident_id: a for a in pending}

    results = []
    for acc_id, amb_id in assignment.items():
        amb, acc = ambs[amb_id], accs[acc_id]
        route = best_route(amb.location.lat, amb.location.lon,
                              acc.location.lat, acc.location.lon)
        db.assign_ambulance(acc_id, amb_id)
        db.change_status(acc_id, AccidentStatus.AMBULANCE_ASSIGNED)  # your rulebook checks this
        db.set_ambulance_status(amb_id, AmbulanceStatus.DISPATCHED)
        results.append({
            "accident_id": acc_id,
            "ambulance_id": amb_id,
            "strategy": strategy,
            "distance_km": route["distance_km"] if route else None,
            "eta_min": route["estimated_time_min"] if route else None,
            "source": route["source"] if route else None
        })
    return results