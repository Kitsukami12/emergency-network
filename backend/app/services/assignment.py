import networkx as nx

from app.core.schemas import Accident, Ambulance
from app.services.routing import get_graph, snap_to_node

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def travel_time_matrix(ambulances: list[Ambulance], accidents: list[Accident]):
    """matrix[i][j] = seconds for ambulance i to reach accident j (None if unreachable)."""
    G = get_graph()
    goal_nodes = [snap_to_node(a.location.lat, a.location.lon) for a in accidents]
    matrix = []
    for amb in ambulances:
        start = snap_to_node(amb.location.lat, amb.location.lon)
        times = nx.single_source_dijkstra_path_length(G, start, weight="travel_time")
        matrix.append([times.get(n) for n in goal_nodes])
    return matrix


def assign_nearest(ambulances, accidents):
    """Greedy: most severe accident first, each takes the closest free ambulance.
    Returns {accident_id: ambulance_id}. Accidents with no free ambulance are left out."""
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