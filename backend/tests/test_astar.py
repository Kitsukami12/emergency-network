import random
import networkx as nx
from app.services.astar import astar
from app.services.routing import get_graph
from app.services.astar import route_between


def test_matches_networkx_on_random_pairs():
    G = get_graph()
    nodes = list(G.nodes)
    rng = random.Random(42)
    for _ in range(30):
        a, b = rng.sample(nodes, 2)
        mine, _ = astar(a, b)
        theirs = nx.shortest_path_length(G, a, b, weight="travel_time")
        assert abs(mine - theirs) < 1e-6



def test_route_between_returns_summary():
    r = route_between(22.7586, 75.8889, 22.72, 75.86)
    assert r is not None
    assert 3 < r["distance_km"] < 12
    assert r["estimated_time_min"] > 0
    assert len(r["route"]) > 10