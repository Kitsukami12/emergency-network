import networkx as nx
import numpy as np
from scipy.optimize import linear_sum_assignment

from app.core.schemas import Accident, Ambulance
from app.services.routing import get_graph, snap_to_node

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

# Mild weights: one extra minute at a CRITICAL scene costs 3x a minute at a LOW one.
# This favours severe cases without sacrificing many minor ones to save one critical.
SEVERITY_WEIGHT = {"LOW": 1.0, "MEDIUM": 1.5, "HIGH": 2.0, "CRITICAL": 3.0}

UNREACHABLE = 1_000_000   # large finite penalty, never infinity
SKIP_PENALTY = 100_000    # cost (seconds, before weighting) of leaving an accident unserved.
                          # Must exceed any real travel time so serving always beats skipping.


def severity_weight(accident: Accident) -> float:
    return SEVERITY_WEIGHT[accident.severity.value]


_times_cache = {}


def times_from(node):
    """Travel time in seconds from `node` to every junction. Cached."""
    if node not in _times_cache:
        _times_cache[node] = nx.single_source_dijkstra_path_length(
            get_graph(), node, weight="travel_time")
    return _times_cache[node]


def travel_time_matrix(ambulances: list[Ambulance], accidents: list[Accident]):
    """matrix[i][j] = seconds for ambulance i to reach accident j (None if unreachable)."""
    goal_nodes = [snap_to_node(a.location.lat, a.location.lon) for a in accidents]
    matrix = []
    for amb in ambulances:
        times = times_from(snap_to_node(amb.location.lat, amb.location.lon))
        matrix.append([times.get(n) for n in goal_nodes])
    return matrix


def assign_nearest(ambulances, accidents):
    """Greedy baseline: most severe accident first, each takes the closest free ambulance.
    Returns {accident_id: ambulance_id}. Accidents with no free ambulance are left out."""
    if not ambulances or not accidents:
        return {}
    matrix = travel_time_matrix(ambulances, accidents)
    order = sorted(range(len(accidents)),
                   key=lambda j: (SEVERITY_ORDER[accidents[j].severity.value],
                                  accidents[j].reported_at))
    taken = set()
    result = {}
    for j in order:
        candidates = [(matrix[i][j], i) for i in range(len(ambulances))
                      if i not in taken and matrix[i][j] is not None]
        if not candidates:
            continue
        _, i = min(candidates)
        taken.add(i)
        result[accidents[j].accident_id] = ambulances[i].ambulance_id
    return result


def assign_hungarian(ambulances, accidents):
    """Optimal pairing: minimise total severity-weighted travel time.
    Returns {accident_id: ambulance_id}.

    When there are fewer ambulances than accidents, "dummy ambulances" are added.
    Giving an accident a dummy means leaving it unserved, which costs SKIP_PENALTY * weight,
    so heavier accidents are the last to be skipped."""
    if not ambulances or not accidents:
        return {}
    n_amb, n_acc = len(ambulances), len(accidents)
    matrix = travel_time_matrix(ambulances, accidents)
    weights = [severity_weight(a) for a in accidents]

    real = np.array([
        [UNREACHABLE if t is None else t * weights[j] for j, t in enumerate(row)]
        for row in matrix
    ], dtype=float)
    # one dummy row per accident, so every accident can always be "skipped"
    dummy = np.array([[SKIP_PENALTY * w for w in weights]] * n_acc, dtype=float)
    cost = np.vstack([real, dummy])          # shape: (n_amb + n_acc, n_acc)

    rows, cols = linear_sum_assignment(cost)
    result = {}
    for i, j in zip(rows, cols):
        if i < n_amb and matrix[i][j] is not None:   # real ambulance, reachable
            result[accidents[j].accident_id] = ambulances[i].ambulance_id
    return result