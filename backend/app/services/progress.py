"""Timed journey for dispatched incidents (a demo-time simulation, not real GPS).

When dispatch assigns an ambulance it reports an ETA. From that ETA this module plans:
  - the crew sets off a few seconds after assignment (EN_ROUTE),
  - the incident is done (RESOLVED) at ETA +/- 2 minutes, one minute after ARRIVED,
  - the ambulance drives back and is AVAILABLE again after about another ETA +/- 2 minutes.
Set DEMO_SPEED=4 to run everything four times faster for a live demo (default 1 = real time).
Plans live in memory. After a restart, incidents already assigned get a default ETA from that
moment, and ambulances left busy are released after a short while, so nothing stays stuck."""
import os
import random
import time

from app.core import db
from app.core.enums import AccidentStatus, AmbulanceStatus

DEMO_SPEED = max(float(os.getenv("DEMO_SPEED", "1")), 0.01)
DEFAULT_ETA_MIN = 6.0     # used when an incident was assigned before this process started
JITTER_MIN = 2.0

_ORDER = [AccidentStatus.AMBULANCE_ASSIGNED, AccidentStatus.EN_ROUTE,
          AccidentStatus.ARRIVED, AccidentStatus.RESOLVED]
_RETURNING = getattr(AmbulanceStatus, "RETURNING", None)      # older enums may not have it
_BUSY = {s for s in (AmbulanceStatus.AT_SCENE, _RETURNING) if s is not None}

plans: dict = {}       # accident_id -> {"ambulance_id", "move_at", "arrive_at", "done_at", "free_at"}
free_at: dict = {}     # ambulance_id -> time it becomes AVAILABLE again


def _sec(minutes: float) -> float:
    return minutes * 60.0 / DEMO_SPEED


def make_plan(ambulance_id, eta_min, now, rng=random):
    eta = eta_min or DEFAULT_ETA_MIN
    done = max(1.5, eta + rng.uniform(-JITTER_MIN, JITTER_MIN))     # minutes after assignment
    back = max(1.0, eta + rng.uniform(-JITTER_MIN, JITTER_MIN))     # drive back to base
    return {"ambulance_id": ambulance_id,
            "move_at": now + 15.0 / DEMO_SPEED,
            "arrive_at": now + _sec(done - 1.0),
            "done_at": now + _sec(done),
            "free_at": now + _sec(done + back)}


def record(assignments, now=None):
    """Call with the list dispatch_pending() returned, so each journey uses the real ETA."""
    now = time.time() if now is None else now
    for a in assignments or []:
        plans[a["accident_id"]] = make_plan(a["ambulance_id"], a.get("eta_min"), now)


def tick(now=None):
    """Advance every journey that is due. Returns a list of what changed."""
    now = time.time() if now is None else now
    events, active = [], set()
    for acc in db.list_accidents():
        if acc.status not in _ORDER[:3] or not acc.assigned_ambulance_id:
            continue
        amb = acc.assigned_ambulance_id
        plan = plans.get(acc.accident_id)
        if plan is None or plan["ambulance_id"] != amb:
            plan = plans[acc.accident_id] = make_plan(amb, DEFAULT_ETA_MIN, now)
        active.add(amb)
        target = (3 if now >= plan["done_at"] else 2 if now >= plan["arrive_at"]
                  else 1 if now >= plan["move_at"] else 0)
        cur = _ORDER.index(acc.status)
        while cur < target:
            cur += 1
            try:
                db.change_status(acc.accident_id, _ORDER[cur])      # one legal step at a time
            except (LookupError, db.IllegalTransition) as e:
                events.append(f"{acc.accident_id}: could not move to {_ORDER[cur].value} ({e})")
                break                                               # someone else moved it: retry next tick
            events.append(f"{acc.accident_id} -> {_ORDER[cur].value}")
            if _ORDER[cur] == AccidentStatus.ARRIVED:
                db.set_ambulance_status(amb, AmbulanceStatus.AT_SCENE)
            elif _ORDER[cur] == AccidentStatus.RESOLVED:
                db.set_ambulance_status(amb, _RETURNING or AmbulanceStatus.AT_SCENE)
                free_at[amb] = plan["free_at"]
                plans.pop(acc.accident_id, None)
                active.discard(amb)

    for a in db.list_ambulances():                                  # ambulances driving back
        if a.status in _BUSY and a.ambulance_id not in active:
            due = free_at.setdefault(a.ambulance_id, now + _sec(random.uniform(1, 3)))
            if now >= due:
                db.set_ambulance_status(a.ambulance_id, AmbulanceStatus.AVAILABLE)
                free_at.pop(a.ambulance_id, None)
                events.append(f"{a.ambulance_id} is available again")
    return events
