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

def road_type_at(lat: float, lon: float) -> str | None:
    """OSM road class (primary, residential...) of the road nearest this point."""
    G = get_graph()
    n = snap_to_node(lat, lon)
    for _, _, d in G.edges(n, data=True):
        hw = d.get("highway")
        if isinstance(hw, list):
            hw = hw[0]
        if hw:
            return hw
    return None