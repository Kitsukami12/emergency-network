import random
import statistics
from dataclasses import dataclass

from app.core.schemas import Accident, Location
from app.services.assignment import SEVERITY_WEIGHT, times_from
from app.services.routing import get_graph, snap_to_node

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SEV_PROBS = [0.4, 0.3, 0.2, 0.1]     # assumption: minor accidents are most common
TICK_S = 10
SCENE_RANGE_S = (300, 600)           # assumption: 5-10 min on scene


@dataclass
class Incident:
    accident: Accident
    arrival_s: int
    scene_s: int


def make_scenario(seed, n_accidents, duration_s):
    """Same seed -> identical accidents, arrival times and scene times."""
    rng = random.Random(seed)
    G = get_graph()
    nodes = list(G.nodes)
    arrivals = sorted(rng.randrange(duration_s) for _ in range(n_accidents))
    incidents = []
    for k, arr in enumerate(arrivals):
        n = rng.choice(nodes)
        acc = Accident(
            accident_id=f"S{seed}-{k}",
            location=Location(lat=G.nodes[n]["y"], lon=G.nodes[n]["x"]),
            severity=rng.choices(SEVERITIES, SEV_PROBS)[0],
        )
        incidents.append(Incident(acc, arr, rng.randint(*SCENE_RANGE_S)))
    return incidents


def simulate(strategy, ambulances, incidents, max_extra_s=6 * 3600):
    """Run one scenario. Returns a list of per-accident records plus the unserved count."""
    by_id = {i.accident.accident_id: i for i in incidents}
    incoming = list(incidents)            # sorted by arrival
    pending = []                          # waiting Incident objects
    free_at = {a.ambulance_id: 0 for a in ambulances}
    records = []
    t = 0
    end = max(i.arrival_s for i in incidents) + max_extra_s

    while (incoming or pending) and t <= end:
        while incoming and incoming[0].arrival_s <= t:
            pending.append(incoming.pop(0))

        free = [a for a in ambulances if free_at[a.ambulance_id] <= t]
        if pending and free:
            accs = [p.accident for p in pending]
            assignment = strategy(free, accs)
            amb_by_id = {a.ambulance_id: a for a in free}
            for acc_id, amb_id in assignment.items():
                inc, amb = by_id[acc_id], amb_by_id[amb_id]
                start = snap_to_node(amb.location.lat, amb.location.lon)
                goal = snap_to_node(inc.accident.location.lat, inc.accident.location.lon)
                travel = times_from(start)[goal]
                free_at[amb_id] = t + travel + inc.scene_s + travel
                records.append({
                    "response_min": (t + travel - inc.arrival_s) / 60,
                    "wait_min": (t - inc.arrival_s) / 60,
                    "weight": SEVERITY_WEIGHT[inc.accident.severity.value],
                })
                pending.remove(inc)
        t += TICK_S

    return records, len(pending) + len(incoming)


def summarize(records, unserved):
    times = sorted(r["response_min"] for r in records)
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "p90": times[int(0.9 * (len(times) - 1))],
        "max": times[-1],
        "wait": statistics.mean(r["wait_min"] for r in records),
        "weighted": statistics.mean(r["response_min"] * r["weight"] for r in records),
        "unserved": unserved,
    }