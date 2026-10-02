import osmnx as ox

from app.core.config import GRAPH_FILE

_graph = None


def get_graph():
    """Load the road graph once, then reuse it."""
    global _graph
    if _graph is None:
        _graph = ox.load_graphml(GRAPH_FILE)
    return _graph


def snap_to_node(lat: float, lon: float) -> int:
    """Return the id of the road junction closest to this point."""
    G = get_graph()
    return ox.distance.nearest_nodes(G, X=lon, Y=lat)

def snap_distance_m(lat, lon):
    """Return the distance in meters from this point to the nearest road junction."""
    G = get_graph()
    n = snap_to_node(lat, lon)
    return ox.distance.great_circle(lat, lon, G.nodes[n]['y'], G.nodes[n]['x'])

def route_between(lat1, lon1, lat2, lon2):
    """Lat/lon in, route summary out. Returns None if no route."""
    G = get_graph()
    start = snap_to_node(lat1, lon1)
    goal = snap_to_node(lat2, lon2)
    result = astar(start, goal)
    if result is None:
        return None
    seconds, path = result
    # TODO 1: distance_m = sum of the cheapest edge "length" between each
    #         consecutive pair in path (same idea as edge_time in astar)
    # TODO 2: coords = [[G.nodes[n]["y"], G.nodes[n]["x"]] for n in path]
    return {
        "distance_km": round(distance_m / 1000, 2),
        "estimated_time_min": round(seconds / 60, 1),
        "route": coords,
    }